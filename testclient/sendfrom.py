#!/usr/bin/env python
import time

from google.cloud import pubsub_v1
from google.oauth2 import service_account

import sys
import json
from pprint import pprint




credentials = service_account.Credentials.from_service_account_file("google-cloud-credentials.json")
publisher = pubsub_v1.PublisherClient(credentials=credentials)
topic_path = publisher.topic_path(credentials.project_id, "ingestion")

if len(sys.argv) != 2:
    print("I need a file from")
    sys.exit(1)


while True:
    data = json.loads(open(sys.argv[1], 'r').read())

    for device in data:

        pprint(device)
        future = publisher.publish(topic_path, json.dumps(device).encode("utf-8"), contentType="text/json")
        print(future.result())

        time.sleep(1)

