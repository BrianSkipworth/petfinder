# Petfetcher
#### _An AWS Lambda function written in Python to get the pets listed on Petfinder.com that are available for adoption from a specific animal rescue organization_

This script generates a static web page that can be shown in an iframe on the organization's existing website. Schedule the function to run as frequently as needed, for most scenarios a nightly run is more than adequate. If run nightly, staff can expect that any animals they add to Petfinder will appear on the website the following day. This script uses only AWS services, including:

- Lambda to run the script that gets the list
- S3 to store the static web page that shows the animals
- EventBridge to schedule regular updates to the page (manually configured separate from this code)

Almost all configuration details that are specific to the organization are stored in environment variables. This enables the script can be set up for a new rescue organization easily and allows information that may change can be updated without needing to edit the code.
