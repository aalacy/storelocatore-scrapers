import requests
import sgzip
import os

session = requests.Session()
proxy_password = os.environ["PROXY_PASSWORD"]
proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
proxies = {
    'http': proxy_url,
    'https': proxy_url
}
session.proxies = proxies

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
	
    headers = {
        'authority': 'kwikkaronline.com',
        'path': '/wp-admin/admin-ajax.php',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://kwikkaronline.com',
        'referer': 'https://kwikkaronline.com/store-locator/',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    form_data = 'action=locate&address=77005&formatted_address=Houston%2C+TX+77005%2C+USA&locatorNonce=a1c3d6f397&distance=25&latitude=29.7183467&longitude=-95.43061410000001&unit=miles&geolocation=false&allow_empty_address=false'
    res = session.post("https://kwikkaronline.com/wp-admin/admin-ajax.php", headers=headers, data=form_data)
    print(res)
    print(res.text)
	
fetch_data()
