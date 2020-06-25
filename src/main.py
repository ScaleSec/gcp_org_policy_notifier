'''
This Cloud Function compares the old available Organization Policies
to the current Organization Policies and determines if there are updates.
'''

import sys
import base64
import os
import googleapiclient.discovery # pylint: disable=import-error
from google.cloud import storage # pylint: disable=import-error


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
    new_policies = list_org_policies()
    old_policies = fetch_old_policies()

    # Sort Both Lists
    new_policies.sort()
    old_policies.sort()

    # Compare Sorted Lists
    if new_policies == old_policies:
        print("No new Org Policies Detected.")
    else:
        print("New Org Policies Detected!")
        print(list(set(new_policies) - set(old_policies)))

        # Updates the GCS bucket to create our new baseline
        update_old_policies()


def list_org_policies():
    '''
    List the available Organization Policies
    '''

    service = googleapiclient.discovery.build("cloudresourcemanager", 'v1')

    # Configures the API request
    request = service.organizations().listAvailableOrgPolicyConstraints(resource="organizations/948721840059")

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
    '''
    Grabs the old Organization Policies from a GCS bucket.
    '''
    # Set our GCS vars, these come from the terraform.tfvars file
    bucket_name = os.environ['POLICY_BUCKET']
    source_blob_name = os.environ['POLICY_FILE']
    destination_file_name = os.environ['FILE_LOCATION']

    policies = list_org_policies()

    # Create the GCS client
    storage_client = storage.Client()

    # Create our bucket variable
    bucket = storage_client.bucket(bucket_name)

    # Create our file name
    blob = bucket.blob(source_blob_name)

    # List the objects in our GCS bucket
    files = storage_client.list_blobs(bucket)

    # Create a list of file names that we will scan for an old policy file
    file_list = []
    for gcs_file in files:
        file_list.append(gcs_file.name)

    # Check to see if the old policies file already exists
    if source_blob_name in file_list:
        # Pulldown the baseline Org policy file
        blob.download_to_filename(destination_file_name)

        # Read contents of old policy file and turn into a list for comparison
        # We turn into a list because thats how we write the contents of list_old_policies()
        with open(f"{destination_file_name}", 'r') as policy_file:
            old_policies = [line.rstrip() for line in policy_file]
        
        return old_policies
    else:
        # Write the new policy baseline to a local file by converting from a list
        # to a multi-line string file
        with open(f"{destination_file_name}", 'w') as policy_file:
            policy_file.write('\n'.join(policies))

        # Upload the baseline Organization Policy file to GCS
        blob.upload_from_filename(destination_file_name)

        # We have now determined this is the first run and can exit.
        print("First run - nothing to compare against.")
        sys.exit(0)

def update_old_policies():
    '''
    Uploads the new Org Policy baseline to the GCS bucket
    '''
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

    print("New Policies Uploaded.")
