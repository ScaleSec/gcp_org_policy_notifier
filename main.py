#!/usr/bin/env python

import sys
import googleapiclient.discovery # pylint: disable=import-error


old_org_policies = ['constraints/cloudfunctions.requireVPCConnector', 'constraints/compute.disableGuestAttributesAccess', 'constraints/compute.restrictVpcPeering', 'constraints/iam.allowedPublicCertificateTrustedRootCA', 'constraints/compute.disableSerialPortLogging', 'constraints/cloudfunctions.allowedIngressSettings', 'constraints/appengine.disableCodeDownload', 'constraints/compute.skipDefaultNetworkCreation', 'constraints/gcp.disableCloudLogging', 'constraints/iam.automaticIamGrantsForDefaultServiceAccounts', 'constraints/compute.requireShieldedVm', 'constraints/compute.requireConfidentialVm', 'constraints/sql.restrictPublicIp', 'constraints/iam.allowedPolicyMemberDomains', 'constraints/iam.disableServiceAccountKeyCreation', 'constraints/storage.uniformBucketLevelAccess', 'constraints/iam.disableWorkloadIdentityClusterCreation', 'constraints/compute.vmCanIpForward', 'constraints/compute.disableNestedVirtualization', 'constraints/serviceuser.services', 'constraints/compute.restrictSharedVpcHostProjects', 'constraints/sql.restrictAuthorizedNetworks', 'constraints/cloudfunctions.allowedVpcConnectorEgressSettings', 'constraints/storage.retentionPolicySeconds', 'constraints/compute.requireOsLogin', 'constraints/compute.storageResourceUseRestrictions', 'constraints/compute.restrictSharedVpcSubnetworks', 'constraints/compute.disableInternetNetworkEndpointGroup', 'constraints/gcp.resourceLocations', 'constraints/compute.trustedImageProjects', 'constraints/compute.vmExternalIpAccess', 'constraints/compute.disableSerialPortAccess', 'constraints/iam.disableServiceAccountCreation', 'constraints/sql.disableDefaultEncryptionCreation', 'constraints/iam.disableServiceAccountKeyUpload', 'constraints/compute.restrictXpnProjectLienRemoval']

def start():
    list_org_policy()
    compare_policies(old_org_policies)

def list_org_policy():
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
    policies = []
    for key in constraints:
        policies.append(key['name'])

    return policies

def compare_policies(old_org_policies):
    '''
    Compares the old constraints vs the new ones.
    '''
    
    new_policies = list_org_policy()
    old_policies = old_org_policies

    # Sort Both Lists
    new_policies.sort()
    old_policies.sort()

    # Compare Sorted Lists
    if new_policies == old_policies:
        print("No new Org Policies")
    else:
        print("New Org Policies Detected!")
        print(list(set(new_policies) - set(old_policies)))


if __name__ == "__main__":
    start()
