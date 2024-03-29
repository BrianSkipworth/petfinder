import boto3
import os
import requests

# Get environment variables
bucket_name = os.environ['BUCKET']
client_id = os.environ['CLIENT']
client_secret = os.environ['SECRET']
default_img = os.environ['IMG'] # URL of an image to show if none is available for the animal
form_url = os.environ['FORM'] # Full URL of the page with the adoption form including the query param ?animal_name=
org_id = os.environ['ORG'] # The sanctuary's Organization ID on Petfinder in lowercase, e.g. 'ca3085'

def extract_animal(animals_response):
    data = animals_response.json()

    # Extract the animal name and primary photo
    animal_info = []
    for animal in data['animals']:
        animal_name = animal['name']
        if 'primary_photo_cropped' in animal and 'small' in animal['primary_photo_cropped']:
            animal_photo_small = animal['primary_photo_cropped']['small']
        else:
            animal_photo_small = "Photo not available"
        animal_info.append(dict([('name',animal_name),('photo',animal_photo_small)]))

    return animal_info

def make_html(animals_list):    
    html =  "<html>\n<head></head>\n<style>p { margin: 40px 0 20px 0 !important; text-align: center; font-size: 16px; font-family: \"Open Sans\",sans-serif } a.button{ -webkit-appearance: button; -moz-appearance: button; appearance: button; display: inline; text-decoration: none; color: #fff; background-color: #e2737e; margin: 20px; border-radius: 20px; min-width: 200px !important; padding: 10px; }</style>\n<body>\n"

    for line in animals_list:
        name = line.get('name', 'Oops!')
        photo = line.get('photo', default_img)
        para = '<p><img src="' + photo + '" style="padding-bottom:10px;"><br>' + name + '<br><br><br><a href="' + form_url + name + '" target="_blank" class="button">Apply to Adopt</a></p>\n'
        html += para

    html += "\n</body>\n</html>"
    return html

def s3_write(animals_html):
    file_contents = animals_html.encode("utf-8")
    file_name = "animals.html"
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=file_name, Body=file_contents, ContentType="text/html", ContentDisposition="inline")

    return "Success"

# Step 1: Obtain the Bearer token
oauth_url = 'https://api.petfinder.com/v2/oauth2/token'
oauth_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret
}
oauth_response = requests.post(oauth_url, data=oauth_data)
if oauth_response.status_code == 200:
    access_token = oauth_response.json()['access_token']

    # Step 2: Call the Petfinder API /animals endpoint
    animals_url = f'https://api.petfinder.com/v2/animals?organization={org_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    animals_response = requests.get(animals_url, headers=headers)

    # Step 3: Format the list as HTML and write to a file on S3
    if animals_response.status_code == 200: # Successful call
        animal_info = extract_animal(animals_response)
        animals_html = make_html(animal_info)
        s3_write(animals_html)
    else:
        print(f"Failed to retrieve data from /animals endpoint. Status code: {animals_response.status_code}")
else:
    print(f"Failed to obtain access token. Status code: {oauth_response.status_code}")

def lambda_handler(event, context):
    print(context.function_name, "ran successfully")
