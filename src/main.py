#!/usr/bin/env python3

"""
This Cloud Function compares the old available Organization Policies
to the current Organization Policies and determines if there are updates.
"""

import base64
import os
import sys
import json
import requests # pylint: disable=import-error
import googleapiclient.discovery # pylint: disable=import-error
from google.cloud import storage # pylint: disable=import-error
from google.cloud import secretmanager # pylint: disable=import-error
from google.api_core import exceptions # pylint: disable=import-error


def announce_kickoff(event, context):
    """
    Announces the start of the org policy comparison function.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    # Starts Logic

    # Creates our two Org Policies lists for comparison
    new_policies = list_org_policies()
    old_policies = fetch_old_policies()

    compare_policies(new_policies, old_policies)

def compare_policies(new_policies, old_policies):
    """
    Compares the old constraints vs the new ones.
    """

    # Sort Both Lists
    new_policies.sort()
    old_policies.sort()

    # Compare Sorted Lists
    if new_policies == old_policies:
        print("No new Org Policies Detected.")
        return False
    else:
        print("New Org Policies Detected!")
        policies = list(set(new_policies) - set(old_policies))
        # Posts new policies to slack channel
        post_to_slack(policies)
        # Updates the GCS bucket to create our new baseline
        upload_policy_file()
        return True

def list_org_policies():
    """
    List the available Organization Policies
    """

    # Grab the Organization ID from the CFN Environment Var
    org_id = os.environ['ORG_ID']

    # Create Cloud Resource Manager API Service
    service = googleapiclient.discovery.build("cloudresourcemanager", 'v1')

    # Configures the API request
    request = service.organizations().listAvailableOrgPolicyConstraints(resource=f"organizations/{org_id}")

    # Execute the API request and display any errors
    try:
        response = request.execute()
    except Exception as e:
        print(e)
        sys.exit(1)

    # Grab all of the constraints from the response
    constraints = response['constraints']

    # Create New Org Policies list
    # We create a list here to more easily sort and compare in compare_policies()
    policies = []
    for key in constraints:
        policies.append(key['name'])

    return policies

def fetch_old_policies():
    """
    Grabs the old Organization Policies from a GCS bucket.
    """
    # Set our GCS vars, these come from the terraform.tfvars file
    bucket_name = os.environ['POLICY_BUCKET']
    source_blob_name = os.environ['POLICY_FILE']

    # Create the GCS client
    storage_client = storage.Client()

    # Create our bucket variable
    bucket = storage_client.bucket(bucket_name)

    # List the objects in our GCS bucket
    files = storage_client.list_blobs(bucket)

    # Create a list of file names that we will scan for an old policy file
    file_list = []
    for gcs_file in files:
        file_list.append(gcs_file.name)

    # Check for pre-existing Org Policy FIle in GCS
    if source_blob_name in file_list:
        old_policies = download_policy_file()
        return old_policies
    # If file does not exist, create and upload
    else:
        upload_policy_file()

def upload_policy_file():
    """
    Uploads the new Org Policy baseline to the GCS bucket
    """
    # Grabs our new baseline in a list format
    new_policies = list_org_policies()

    # Set our GCS vars, these come from the terraform.tfvars file
    bucket_name = os.environ['POLICY_BUCKET']
    source_file_name = os.environ['FILE_LOCATION']
    destination_blob_name = os.environ['POLICY_FILE']

    # Create the GCS client
    storage_client = storage.Client()

    # Write the new policies to our local file by converting from a list
    # to a multi-line string file
    with open(f"{source_file_name}", 'w') as policy_file:
        policy_file.write('\n'.join(new_policies))

    # Upload the new Organization Policy file to GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    print("New Policies Uploaded. Exiting.")
    sys.exit(0)

def download_policy_file():
    """
    Downloads the Org Policy baseline from the GCS bucket
    """
    # Set our GCS vars, these come from the terraform.tfvars file
    bucket_name = os.environ['POLICY_BUCKET']
    source_blob_name = os.environ['POLICY_FILE']
    destination_file_name = os.environ['FILE_LOCATION']

    # Create the GCS client
    storage_client = storage.Client()

    # Create our bucket via the GCS client
    bucket = storage_client.bucket(bucket_name)

    # Creates our gcs -> prefix -> file variable
    blob = bucket.blob(source_blob_name)

    # Pulldown the baseline Org policy file
    blob.download_to_filename(destination_file_name)

    # Read contents of old policy file and turn into a list for comparison
    # We turn into a list because thats how we write the contents of list_org_policies()
    with open(f"{destination_file_name}", 'r') as policy_file:
        old_policies = [line.rstrip() for line in policy_file]
    print("Org Policy File Downloaded from GCS Bucket")

    return old_policies

def post_to_slack(policies):
    """
    Posts to a slack channel with the new GCP Org Policies
    """

    # Slack webhook URL
    url = fetch_slack_webhook()

    # Set the headers for our slack HTTP POST
    headers = {
        'Content-Type': 'application/json'
    }

    # We want to iterate through the policies and convert to JSON
    for policy in policies:
        # This makes the policy into a dict. Slack requires the format {"text": "data"}
        dict_policy = {"text": f"New Organization Policy Detected: {policy}"}
        # Converts to JSON for the HTTP POST payload
        payload = json.dumps(dict_policy)
        # Post to the slack channel
        try:
            requests.request("POST", url, headers=headers, data=payload)
        except Exception as e:
            print(e)
            sys.exit(1)

def fetch_slack_webhook():
    """
    Grabs the Slack Webhook URL from GCP Secret Manager.
    """
    secret_project = getenv('S_PROJECT')
    secret_name = getenv('S_NAME')
    secret_version = getenv('S_VERSION', "latest")
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Set the secret location
    secret_location = client.secret_version_path(secret_project, secret_name, secret_version)

    # Get the secret Slack Webhook secret to use in send_email()
    try:
        response = client.access_secret_version(secret_location)
        slack_webbook = response.payload.data.decode('UTF-8').rstrip()
        return slack_webbook
    except exceptions.FailedPrecondition as e:
        print(e)

if __name__ == "__main__":
    announce_kickoff("testing", None)