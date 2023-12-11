from azure.identity import ClientSecretCredential
from azure.mgmt.subscription import SubscriptionClient

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

    subscriptions = subscription_client.subscriptions.list()

    data_row = []
    for subscription in subscriptions:
        sub_id = subscription.id.split('/')[-1]
        display_name = subscription.display_name
        state = subscription.state
        authorization_source = subscription.authorization_source

        data_row.append([sub_id, display_name, state, authorization_source])

    if data_row:
        with open('subscription_details.csv', 'w', newline='') as csv_file:
            csv_header = [
                'Subscription id', 'Subscription name', 'State', 'Authorization Source'
            ]

            writer = csv.writer(csv_file)
            writer.writerow(csv_header)
            writer.writerows(data_row)

        print('Data successfully processed.')

except:
    print('Error occured.')
