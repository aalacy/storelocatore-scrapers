import csv
import requests
from sgrequests import SgRequests
import ssl
import certifi
import http.client as http_client
from sgselenium import SgSelenium

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Authorization": "Bearer hIWHFeDpkoBaIxwB9wsaVD9SrxRSVU",
    "Host": "api.7-eleven.com",
    "Origin": "https://www.7-eleven.com",
    "Referer": "https://www.7-eleven.com/",
    "X-SEI-PLATFORM": "us_web",
    "X-SEI-TRIP-IDs": "Y2QwNGJiMDlkNzZkZDljYmQ5YzZlYzM4OTRlOGVkMjU=",
    "X-SEI-TZ": "-07:00",
    "X-SEI-VERSION": "3.6.0",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36"
}

def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)


def override_retries():
    # monkey patch sgrequests in order to set max retries ...
    # we will control retries in this script in order to reset the session and get a new IP each time
    import requests  # ignore_check

    def new_init(self):
        requests.packages.urllib3.disable_warnings()
        self.session = self.requests_retry_session(retries=0)

    SgRequests.__init__ = new_init


override_retries()

def get(url):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)
    certs_path = certifi.where()
    certs_path = '/usr/local/etc/openssl/cert.pem'
    print(certs_path)
    context.load_verify_locations(cafile=certs_path)
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    conn = http_client.HTTPSConnection("api.7-eleven.com", context=context)
    print("connecting")
    conn.connect()
    print("connected")
    conn.request("GET", url, headers=HEADERS)
    print("requesting")
    res = conn.getresponse()
    return res.read()

def fetch_data():
    api_template = "https://api.7-eleven.com/v4/stores?lat=37.76182419999999&lon=-122.3985871&radius=50&curr_lat=37.76182419999999&curr_lon=-122.3985871&features="
    driver = SgSelenium().chrome()
    driver._client.set_header_overrides(headers=HEADERS)
    driver.get(api_template)
    print(driver.page_source)
    #response = requests.get(api_template, headers=HEADERS)
    #print(get(api_template))
    yield [
        website,
        loc,
        name,
        add,
        city,
        state,
        zc,
        country,
        store,
        phone,
        typ,
        lat,
        lng,
        hours,
    ]


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
