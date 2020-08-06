import time
from sgrequests import SgRequests
import urllib.parse
import simplejson as json
import simple_scraper_pipeline as scrape_pipeline

def fetch_data():
    """
    Fetches the data from an external source, conforming to the signature described in `scrape_pipeline.define_and_run`
    :return:
        A list of dicts, each of which is the raw data field.
    """

    locations_url = "https://svc.moxiworks.com/service/v1/profile/offices/search"
    ms_since_epoch = int(time.time() * 1000)
    params = urllib.parse.urlencode({
        "center_lat": 34.014959683598164,
        "center_lon": -118.4117215,
        "order_by": "distance",
        "company_uuid": "1234567",
        "callback": "jQuery22407851157122881546_1596651612792",
        "source": "agent % 20",
        "website": "",
        "source_display_name": "Windermere.com",
        "_": ms_since_epoch
    })

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'cache-control': 'max-age=0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    }

    session = SgRequests()
    response = session.get(locations_url, data=params, headers=headers)

    json_result = json.loads(urllib.parse.unquote(response.text), encoding="utf8")

    result_status = str(json_result['status'])
    if result_status != "success":
        print("API call is not successful; result status: " + result_status)
        print("Printing result:")
        print(json.dumps(json_result, indent=2))
        raise Exception("API call is not successful; result status: " + result_status)

    return json_result['data']['result_list']

def strip_extension(phone: str):
    """
    Strips the phone's extension (after and including the "x"), and returns the phone number.
    """
    return phone.split("x")[0]

def phone_number_extract(raw: str, which_index=0):
    """
    Attempts to extract a raw phone number from a string in which phone numbers are delimited by "/",
    And extensions are present as e.g. "x12345"
    :param raw:
        The raw phone number.
    :param which_index:
        Which of the present phone numbers to take?
        Defaults to 0 (first one.)
    :return:
        The phone number, or an empty string if none exist at the given index.
    """
    split_phones = raw.split("/")
    try:
        return strip_extension(split_phones[which_index])
    except ValueError:
        return ""

def scrape():
    """
    The main entrypoint into the program.
    """

    record_mapping = {
        "location_name": [["name"]],
        "street_address": [["location", "address"], ["location", "address2"]],
        "city": [["location", "city"]],
        "state": [["location", "state"]],
        "zip": [["location", "zip"]],
        "country_code": [["location", "country_code"]],
        "store_number": [["external_id"]],
        "phone": [["phone"]],
        "location_type": [["legal"]],
        "latitude": [["location", "latitude"]],
        "longitude": [["location", "longitude"]],
    }

    constant_fields = {
        "locator_domain": "https://windermere.com",
        "page_url": "<MISSING>",
        "hours_of_operation": "<MISSING>"
    }

    required_fields = [
        "street_address",
        "city",
        "state"
    ]

    field_transformers = {
        "phone": lambda s: phone_number_extract(s)
    }

    scrape_pipeline.define_and_run( data_fetcher= lambda: fetch_data(),
                                    record_mapping=record_mapping,
                                    constant_fields=constant_fields,
                                    required_fields=required_fields,
                                    field_transform=field_transformers,
                                    fail_on_outlier=False)

scrape()
