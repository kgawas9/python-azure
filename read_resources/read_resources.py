from azure.identity import ClientSecretCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient

from decouple import config

import csv

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

        resource_groups = resource_client.resource_groups.list()

        # resource details
        for resource_group in resource_groups:
            resource_group_name = resource_group.name
            resource_group_location = resource_group.location

            resources = resource_client.resources.list_by_resource_group(resource_group_name=resource_group_name)

            for resource in resources:
                # print(f'{resource}/n')
                resource_name = resource.name
                resource_type = resource.type.split('/')[-1]

                resource_tag_keys = resource.tags.keys()

                resource_tags = {}
                for key in resource_tag_keys:
                    resource_tags[key] = resource.tags.get(key)

                resource_tags = ', '.join(f'{key}:{value}' for key, value in resource_tags.items())
                

            data_row.append([sub_id, display_name, state, authorization_source, resource_group_name, resource_group_location, resource_name, resource_type, resource_tags])


        if data_row:
            with open('subscription_details.csv', 'w', newline='') as csv_file:
                csv_header = [
                    'Subscription id', 'Subscription name', 'State', 'Authorization source', 'Resource group name', 'Resource group location', 
                    'Resource name', 'Resource type', 'Resource tags'
                ]

                writer = csv.writer(csv_file)
                writer.writerow(csv_header)
                writer.writerows(data_row)

            print('Data successfully processed.')

except:
    print('Error occured.')
