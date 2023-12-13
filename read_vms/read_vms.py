from azure.identity import ClientSecretCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient

from decouple import config

import csv
from datetime import datetime

tenant_id = config('tenant_id')
client_id = config('client_id')
client_secret = config('client_secret')

try:
    credentials = ClientSecretCredential(tenant_id=tenant_id,
                                        client_id=client_id,
                                        client_secret=client_secret)

    subscription_client = SubscriptionClient(credential=credentials)

    # List of subscriptions
    subscriptions = subscription_client.subscriptions.list()

    data_row = []

    for subscription in subscriptions:
        # subscription details
        sub_id = subscription.id.split('/')[-1]
        display_name = subscription.display_name
        state = subscription.state
        authorization_source = subscription.authorization_source

        # resource groups
        resource_client = ResourceManagementClient(
            credential=credentials, subscription_id=sub_id
        )

        compute_client = ComputeManagementClient(
            credential=credentials, subscription_id=sub_id
        )

        resource_groups = resource_client.resource_groups.list()

        # resource details
        for resource_group in resource_groups:
            resource_group_name = resource_group.name
            resource_group_location = resource_group.location

            virtual_machines = compute_client.virtual_machines.list(resource_group_name=resource_group_name)

            for virtual_machine in virtual_machines:
                vm_name = virtual_machine.name
                # vm_storage_profile = virtual_machine.storage_profile
                vm_id = virtual_machine.vm_id
                vm_created = datetime.strftime(virtual_machine.time_created, '%d-%b-%Y %H:%M:%S')

                data_row.append([sub_id, display_name, state, authorization_source, resource_group_name, resource_group_location, vm_id, vm_name, vm_created])


    if data_row:
        with open('vm_details.csv', 'w', newline='') as csv_file:
            csv_header = [
                'Subscription id', 'Subscription name', 'State', 'Authorization source', 'Resource group name', 'Resource group location', 
                'VM id', 'VM name', 'VM created on'
            ]

            writer = csv.writer(csv_file)
            writer.writerow(csv_header)
            writer.writerows(data_row)

        print('Data successfully processed.')

except Exception as e:
    print('Error occured.', e)
