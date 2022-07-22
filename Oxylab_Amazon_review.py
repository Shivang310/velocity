import requests
from pprint import pprint
import time
start_time = time.time()
# Structure payload.B00Q6P4CMA
respon_time =[]
for num in range(1,401):
    payload = {
        'source': 'amazon_reviews',
        'domain': 'com',
        'query': 'B00Q6P4CMA',
        'start_page': num
    }


    # Get response.
    response = requests.request(
        'POST',
        'https://realtime.oxylabs.io/v1/queries',
        auth=('shorthillstech', 'BQ2RyVFxHRdr'),
        json=payload,
    )

    # Print prettified response to stdout.
    try:
        pprint(response.text)
    except Exception as e:
        print(e)
    print("--- %s seconds ---" % (time.time() - start_time))
    respon_time.append("--- %s seconds ---" % (time.time() - start_time))
print(respon_time)
print("--- %s seconds ---" % (time.time() - start_time))