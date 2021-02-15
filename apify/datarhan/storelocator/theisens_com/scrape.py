import csv
import json
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgFirefox


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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
    items = []

    DOMAIN = "theisens.com"
    start_url = "https://www.theisens.com/ProxyRequest.aspx"

    formdata = {
        "url": "/api/branchlocator/search/geolocation",
        "data": '{"coordinates":{"latitude":39.4667,"longitude":-0.7167},"range":0,"defaultStoreId":null,"useDefaultLocationIfNoResults":false}',
        "contentType": "application/json",
        "method": "POST",
    }
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "authorization": "Bearer null",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": "visid_incap_1461359=a0oa7KOyTWK3s9oHNyvQFeBqFWAAAAAAQUIPAAAAAADvRdsBZz1vo7RNLcwPuZ+5; incap_ses_1396_1461359=um8XJE2M10bPNUo1ppZfE+JqFWAAAAAAZGzb0KkOA9oAxvUq5LGLKw==; _gcl_au=1.1.858541093.1612016356; _ga=GA1.2.722660489.1612016358; _gid=GA1.2.1945811165.1612016358; _gat=1; _fbp=fb.1.1612016359071.1929352260; _hjTLDTest=1; _hjid=69cf75c8-d026-42da-90c1-73933eb9ca62; _hjFirstSeen=1; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _hjIncludedInSessionSample=1; visitor_id=d773a3c6-33b1-44e5-b486-7178a6a22933; visit_id=6a558ce9-12cd-4391-8bc1-ddde56aadc6f; __qca=P0-1780273565-1612016360667; BVBRANDID=e7ecab81-2218-480d-b80d-ee009d9e7174; BVBRANDSID=3593b975-1696-4992-95dd-20815fff7337; LiveGuide_zrLE4yysPTrw8FJsnyDi9lDh157Iuntc_date=1612016366315; LiveGuide_zrLE4yysPTrw8FJsnyDi9lDh157Iuntc_url=https%3A%2F%2Fwww.theisens.com%2Fabout-theisens%2Fstore-locator; LiveGuide_zrLE4yysPTrw8FJsnyDi9lDh157Iuntc_title=Store%20Locator%20%7C%20Theisen's%20Home%20%26%20Auto; LiveGuide_zrLE4yysPTrw8FJsnyDi9lDh157Iuntc_ref=; LiveGuide_zrLE4yysPTrw8FJsnyDi9lDh157Iuntc_duration=0; listingView=grid; _uetsid=236a2600630611eb905b05ddd4efd33b; _uetvid=236c8d00630611eb9a8095ff2b2a9b36",
        "origin": "https://www.theisens.com",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["results"]:
        store_url = urljoin(start_url, poi["location"]["customUrl"])
        location_name = poi["location"]["locationName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["location"]["address1"]
        if poi["location"]["address2"]:
            street_address += ", " + poi["location"]["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["location"]["city"]
        city = city if city else "<MISSING>"
        state = poi["location"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["location"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["location"]["country"]
        store_number = "<MISSING>"
        phone = poi["location"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["latitude"]
        longitude = poi["location"]["longitude"]

        with SgFirefox() as driver:
            driver.get(store_url)
            sleep(5)
            loc_dom = etree.HTML(driver.page_source)
        hoo = loc_dom.xpath('//dd[@id="branch-detail-business-hours"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
