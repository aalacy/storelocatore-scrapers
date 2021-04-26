import csv
import json
from lxml import etree

from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests(proxy_rotation_failure_threshold=0).requests_retry_session(
        retries=1,
        backoff_factor=0.3,
        status_forcelist=[
            418,
        ],
    )

    items = []
    scraped_items = []

    DOMAIN = "doitbest.com"
    start_url = "https://doitbest.com/StoreLocator/Submit"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    response = session.get("https://doitbest.com/store-locator", headers=hdr)
    dom = etree.HTML(response.text)
    csrfid = dom.xpath('//input[@id="StoreLocatorForm_CSRFID"]/@value')[0]
    token = dom.xpath('//input[@id="StoreLocatorForm_CSRFToken"]/@value')[0]

    headers = {
        "content-type": "application/json; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-mod-sbb-ctype": "xhr",
        "x-requested-with": "XMLHttpRequest",
    }

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=None,
    )
    for code in all_codes:
        body = {
            "StoreLocatorForm": {
                "Location": code,
                "Filter": "All Locations",
                "Range": "50",
                "CSRFID": csrfid,
                "CSRFToken": token,
            }
        }
        response = session.post(start_url, headers=headers, json=body, verify=False)
        if response.status_code != 200:
            response = session.get("https://doitbest.com/store-locator", headers=hdr)
            dom = etree.HTML(response.text)
            csrfid = dom.xpath('//input[@id="StoreLocatorForm_CSRFID"]/@value')[0]
            token = dom.xpath('//input[@id="StoreLocatorForm_CSRFToken"]/@value')[0]
            body = {
                "StoreLocatorForm": {
                    "Location": code,
                    "Filter": "All Locations",
                    "Range": "50",
                    "CSRFID": csrfid,
                    "CSRFToken": token,
                }
            }
            response = session.post(start_url, headers=headers, json=body, verify=False)
            if not response.text:
                continue
        data = json.loads(response.text)
        if not data["Response"].get("Stores"):
            continue
        all_locations += data["Response"]["Stores"]

    for poi in all_locations:
        store_url = poi["WebsiteURL"]
        store_url = "https://" + store_url if store_url else "<MISSING>"
        try:
            location_name = poi["Name"]
        except TypeError:
            continue
        location_name = location_name if location_name else "<MISSING>"
        passed = False
        if "do it best" in location_name.lower():
            passed = True
        if "doitbest" not in store_url.lower() and not passed:
            continue
        street_address = poi["Address1"]
        if poi["Address2"]:
            street_address += ", " + poi["Address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZipCode"]
        if not zip_code:
            continue
        country_code = "<MISSING>"
        store_number = poi["ID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
