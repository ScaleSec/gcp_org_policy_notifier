#!/usr/bin/env python3

'''
This Cloud Function compares the old available Organization Policies
to the current Organization Policies and determines if there are updates.
'''

import base64
import sys
import json
import datetime # pylint: disable=import-error
import requests # pylint: disable=import-error
import googleapiclient.discovery # pylint: disable=import-error

from os import getenv
from google.cloud import storage # pylint: disable=import-error
from google.cloud import secretmanager # pylint: disable=import-error
from google.api_core import exceptions # pylint: disable=import-error
from github import Github # pylint: disable=import-error


def announce_kickoff(event, context):
    """
    Announces the start of the org policy comparison function.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    # Starts Logic
    compare_policies()

def compare_policies():
    '''
    Compares the old constraints vs the new ones.
    '''

    # Creates our two Org Policies lists for comparison
    old_policies = fetch_old_policies()
    current_policies = constraint_transform()

    # Sort Both Lists
    current_policies.sort()
    old_policies.sort()

    # Compare Sorted Lists
    if current_policies == old_policies:
        print("No new Org Policies Detected.")
    else:
        print("New Org Policies Detected!")
        new_policies = list(set(current_policies) - set(old_policies))

        # Create GitHub PR for new policies
        create_pr_file_content()
        # Posts new policies to slack channel - move somewhere else?
        post_to_slack(new_policies)
        # Updates the GCS bucket to create our new baseline
        upload_policy_file()

def list_org_policies():
    """
    List the available Organization Policies
    """

    # Grab the Organization ID from the CFN Environment Var
    org_id = getenv('ORG_ID')

    # Create Cloud Resource Manager API Service
    service = googleapiclient.discovery.build("cloudresourcemanager", 'v1')

    # Configures the API request
    request = service.organizations().listAvailableOrgPolicyConstraints(resource=f"organizations/{org_id}")

    # Execute the API request and display any errors
    try:
        org_response = request.execute()
    except Exception as e:
        print(e)
        sys.exit(1)

    return org_response

def constraint_transform():
    """
    Transforms our List Org policy response into a list of constraint names for comparison.
    """
    #Grabs our response from the List Org Policy call
    org_response = list_org_policies()

    #Drill into constraints response
    constraints = org_response['constraints']

    # Create New Org Policies list
    # We create a list here to more easily sort and compare in compare_policies()
    current_org_policies = []
    for key in constraints:
        current_org_policies.append(key['name'])

    return current_org_policies

def fetch_old_policies():
    """
    Grabs the old Organization Policies from a GCS bucket.
    """
    # Set our GCS vars, these come from the terraform.tfvars file
    bucket_name = getenv('POLICY_BUCKET')
    source_blob_name = getenv('POLICY_FILE')

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

    # Check for pre-existing Org Policy File in GCS
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
    bucket_name = getenv('POLICY_BUCKET')
    source_file_name = getenv('FILE_LOCATION')
    destination_blob_name = getenv('POLICY_FILE')

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
    bucket_name = getenv('POLICY_BUCKET')
    source_blob_name = getenv('POLICY_FILE')
    destination_file_name = getenv('FILE_LOCATION')

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

def post_to_slack(new_policies):
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
    for policy in new_policies:
        # This makes the policy into a dict. Slack requires the format {"text": "data"}
        dict_policy = {"text": f"New Organization Policy Detected: {policy}"}
        # Converts to JSON for the HTTP POST payload
        payload = json.dumps(dict_policy)
        # Post to the slack channel
        try:
            requests.request("POST", url, headers=headers, data=payload)
            print("Posting to Slack")
        except Exception as e:
            print(e)
            sys.exit(1)

def fetch_slack_webhook():
    """
    Grabs the Slack Webhook URL from GCP Secret Manager.
    """
    # Set GCP Secret Manager vars
    secret_project = getenv('S_PROJECT')
    secret_name = getenv('S_SLACK_NAME')
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

def create_pr_file_content():
    """
    Creates the Organization Policy file content for the GitHub Pull Request.
    """

    #Grabs our response from the List Org Policy call
    org_response = list_org_policies()

    # Create PR file content
    pr_file_content = json.dumps(org_response, indent=4)

    # Create GitHub Pull Request
    create_pr(pr_file_content)

def fetch_github_token():
    """
    Grabs the GitHub Access token from GCP Secret Manager.
    """
    # Set GCP Secret Manager vars
    secret_project = getenv('S_PROJECT')
    secret_name = getenv('S_TOKEN_NAME')
    secret_version = getenv('S_VERSION', "latest")

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Set the secret location
    secret_location = client.secret_version_path(secret_project, secret_name, secret_version)

    # Get the GitHub Token secret to use in create_pr()
    try:
        response = client.access_secret_version(secret_location)
        github_token = response.payload.data.decode('UTF-8').rstrip()
        return github_token
    except exceptions.FailedPrecondition as e:
        print(e)

def create_pr(pr_file_content):
    # Fetch our GitHub token from GCP Secret Manager
    github_token = fetch_github_token()

    # Date is used in PR
    todays_date = datetime.date.today()

    # Create our GitHub authorized client
    g = Github(github_token)

    # Set our target repo
    repo = g.get_repo("ScaleSec/gcp_org_policy_notifier")

    # Identify which file we want to update
    repo_file_path = "policies/org_policy.json"

    # Set our branches
    default_branch = "master"
    target_branch = "new_policies"

    # Create our new branch
    source = repo.get_branch(f"{default_branch}")
    repo.create_git_ref(ref=f"refs/heads/{target_branch}", sha=source.commit.sha)

    # Retrieve the old file to get its SHA and path
    contents = repo.get_contents(repo_file_path, ref=default_branch)

    # Update the old file with new content
    repo.update_file(contents.path, "New Policies Detected", pr_file_content, contents.sha, branch=target_branch)

    # Create our Pull Request
    repo.create_pull(title=f"New Policies Detected on {todays_date}", head=target_branch, base=default_branch, body=f"New Policies Detected on {todays_date}")

if __name__ == "__main__":
    compare_policies()
