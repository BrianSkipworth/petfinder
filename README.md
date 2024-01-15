# :rabbit: Petfetcher
#### _An AWS Lambda function written in Python to get the pets listed on Petfinder.com that are available for adoption from a specific animal rescue organization_

This script generates a static web page that can be shown inside an iframe on the organization's existing website. See the example page for [Herd and Flock Animal Sanctuary](https://herdandflock.s3.us-west-1.amazonaws.com/animals.html). 

Schedule the function to run as frequently as needed, for most scenarios a nightly run is adequate and the rescue staff can expect that any animals they add to Petfinder will appear on the website the following day. This script uses only AWS services, including:

- Lambda to run the script that gets the list
- S3 to store the static web page that shows the animals
- EventBridge to schedule regular updates to the page (manually configured separate from this code)

## Set Up

On AWS create a new S3 bucket and select Access: Public. 

Next create a new Lambda function. The code in lambda.py can be copy-pasted on the Code tab in the Lambda screen, though a few additional steps will be required to add external Python libraries to the Lambda function's runtime environment. Also, to avoid a current issue with a conflict between a necessary library and AWS's boto3 SDK, we have to revert the library to an older version before deploying the Lambda function.

Complete Step 1 described in the Medium post [How to add External Python Libraries to AWS Lambda](https://medium.com/@gauravkachariya/how-to-add-external-python-libraries-to-aws-lambda-499674113fb7)

Before moving on to Step 2, remove the directory for the package `urllib3` which the requests library has installed as a dependency. Then, manually re-install an older version using the command `pip install --upgrade urllib3==1.26.18 -t .`

```
(venv) [cloudshell-user@ip-10-6-25-93 python]$ pip install --upgrade urllib3==1.26.18 -t .
Collecting urllib3==1.26.18
  Using cached urllib3-1.26.18-py2.py3-none-any.whl (143 kB)
Installing collected packages: urllib3
Successfully installed urllib3-1.26.18
```
Now move on and complete Steps 2 and 3.


### Petfinder API
You will need to generate a client and secret. Sign up on their site to get your credentials: https://www.petfinder.com/user/developer-settings/
[Petfinder API Docs](https://www.petfinder.com/developers/v2/docs/)

### Environment Variables
Almost all configuration details that are specific to the rescue organization are stored in environment variables, with the exception of style code to make the generated web page match the rescue's existing website (styling is hardcoded). This enables the script can be set up for a new rescue organization quickly and allows information that may change frequently to be updated without needing to edit the code.

| Key | Value |
|---|---|
| BUCKET | The name of the S3 bucket |
| CLIENT | A Petfinder API Key |
| SECRET | A Petfinder Secret |
| ORG | The sanctuary's Organization ID on Petfinder in lowercase, e.g. 'ca3085' |
| FORM | Full URL of the adoption form including the query param ?animal_name= |


In the function code we begin by retrieving these environment variables.

```python
bucket_name = os.environ['BUCKET']
client_id = os.environ['CLIENT']
client_secret = os.environ['SECRET']
default_img = os.environ['IMG'] # URL of an image to show if none is available for the animal
form_url = os.environ['FORM'] # Full URL of the adoption form including the query param ?animal_name=
org_id = os.environ['ORG'] # The sanctuary's Organization ID on Petfinder in lowercase, e.g. 'ca3085'
```
The rest of the function code is thoroughly commented. 

---
## Planned Enhancements
The Petfetcher function would be easier to monitor if it had built-in alerting to send someone an email when an attempted fetch fails for any reason, and AWS SES service can be used do this.
