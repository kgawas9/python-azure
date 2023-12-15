from azure.identity import ClientSecretCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
from azure.storage.blob import BlobServiceClient

from decouple import config
from pathlib import Path

import csv

tenant_id = config('tenant_id')
client_id = config('client_id')
client_secret = config('client_secret')

account_name = config('account_name')
account_key = config('account_key')
container_name = config('container_name')

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
                try:
                    resource_tag_keys = resource.tags.keys()
                    resource_tags = {}
                    for key in resource_tag_keys:
                        resource_tags[key] = resource.tags.get(key)

                    resource_tags = ', '.join(f'{key}:{value}' for key, value in resource_tags.items())
                except:
                    resource_tags = ''
                    print('No tags found')
                

                data_row.append([sub_id, display_name, state, authorization_source, resource_group_name, resource_group_location, resource_name, resource_type, resource_tags])


    if data_row:
        with open('resource_details.csv', 'w', newline='') as csv_file:
            csv_header = [
                'Subscription id', 'Subscription name', 'State', 'Authorization source', 'Resource group name', 'Resource group location', 
                'Resource name', 'Resource type', 'Resource tags'
            ]

            writer = csv.writer(csv_file)
            writer.writerow(csv_header)
            writer.writerows(data_row)

        


    # upload file to storage account
    local_file_path = Path.cwd().joinpath('resource_details.csv')
    
    blob_service_client = BlobServiceClient(account_url=f'https://{account_name}.blob.core.windows.net', credential=account_key)

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_path)

    with open(local_file_path, 'rb') as data:
        blob_client.upload_blob(data)

    print('Data successfully processed.')

    # Read blob file in memory

    blob_name = 'resource_details.csv'
    downloaded_blob = blob_client.download_blob()
    content = downloaded_blob.readall()
    decoded_content = content.decode('utf-8')

    print(decoded_content)

    with open('from_storage.csv', 'wb') as file:
        downloaded_stream = blob_client.download_blob()
        file.write(downloaded_stream.readall())

    print(f'\nFile successfully saved in {Path.cwd()} directory.')

except Exception as e:
    print('Error occured.', e)
