import requests
import json

url = "https://run.cerebrium.ai/v2/p-94ad0fb9/eth-price-1-hour-predictor/predict"

payload = json.dumps({
    'price_24_hour_ago': 46656.851562,
    'price_23_hour_ago': 46700.535156,
    'price_22_hour_ago': 46700.535156,
    'price_21_hour_ago': 46700.535156,
    'price_20_hour_ago': 46700.535156,
    'price_19_hour_ago': 46700.535156,
    'price_18_hour_ago': 46700.535156,
    'price_17_hour_ago': 46700.535156,
    'price_16_hour_ago': 46700.535156,
    'price_15_hour_ago': 46700.535156,
    'price_14_hour_ago': 46700.535156,
    'price_13_hour_ago': 46700.535156,
    'price_12_hour_ago': 46700.535156,
    'price_11_hour_ago': 46700.535156,
    'price_10_hour_ago': 46700.535156,
    'price_9_hour_ago': 46700.535156,
    'price_8_hour_ago': 46700.535156,
    'price_7_hour_ago': 46700.535156,
    'price_6_hour_ago': 46700.535156,
    'price_5_hour_ago': 46700.535156,
    'price_4_hour_ago': 46700.535156,
    'price_3_hour_ago': 46700.535156,
    'price_2_hour_ago': 46700.535156,
    'price_1_hour_ago': 46700.535156
})

headers = {
  'Authorization': 'public-6fb5d32ac9801938a17b',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)