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

    # Configure the API request
    request = service.organizations().listAvailableOrgPolicyConstraints(resource="organizations/948721840059")

    # Execute the API request and display any errors
    try:
        response = request.execute()
    except Exception as e:
        print(e)
        sys.exit(1)

    # Grab dict
    constraints = response['constraints']

    # Create New Org Policies
    # We create a list here to more easily sort and compare in compare_policies()
    policies = []
    for key in constraints:
        policies.append(key['name'])

    return policies

def fetch_old_policies():
    '''
    Grabs the old Organization Policies from a GCS bucket.
    '''

    # Set vars
    bucket_name = os.environ['POLICY_BUCKET']
    source_blob_name = os.environ['POLICY_FILE']
    destination_file_name = os.environ['FILE_LOCATION']

    # Create the GCS client
    storage_client = storage.Client()

    # Download old Organization Policy file locally
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    # Read contents of old policy file and turn into a list for comparison
    # We turn into a list because thats how we write the contents of list_old_policies()
    with open(f"{destination_file_name}", 'r') as policy_file:
        old_policies = [line.rstrip() for line in policy_file]

    return old_policies

def update_old_policies():
    '''
    Uploads the new Org Policy baseline to the GCS bucket
    '''
    # Grabs our new baseline in list format
    new_policies = list_org_policies()

    bucket_name = os.environ['POLICY_BUCKET']
    source_file_name = os.environ['FILE_LOCATION']
    destination_blob_name = os.environ['POLICY_FILE']

    # Create the GCS client
    storage_client = storage.Client()

    # Write the new policies to our local file by converting from a list
    # to a multi-line string file
    with open(f"{source_file_name}", 'w') as policy_file:
        policy_file.write('\n'.join(new_policies))

    # Upload the new Organization Policy file
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    print("New Policies Uploaded.")
