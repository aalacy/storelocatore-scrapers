import csv
import json
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameters

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
    session = SgRequests()

    items = []

    DOMAIN = "eatandys.com"
    base_url = "https://locations.eatandys.com/"
    start_url = "https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token=WYEMXMEMZMFGMIDG&country=US&multi_account=false"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["locations"]:
        store_url = urljoin(base_url, poi["llp_url"])
        street_address = poi["store_info"]["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["store_info"]["locality"]
        city = city if city else "<MISSING>"
        state = poi["store_info"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["store_info"]["postcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["store_info"]["country"]
        store_number = "<MISSING>"

        loc_url = "https://api.momentfeed.com/v1/analytics/api/llp.json"
        params = {
            "address": street_address,
            "locality": city,
            "multi_account": "false",
            "pageSize": "30",
            "region": state,
        }
        loc_url = add_or_replace_parameters(loc_url, params)
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
            "authorization": "WYEMXMEMZMFGMIDG",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        }
        loc_response = session.get(loc_url, headers=headers)
        data = json.loads(loc_response.text)

        location_name = data[0]["store_info"]["name"]
        phone = data[0]["store_info"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = data[0]["store_info"]["latitude"]
        longitude = data[0]["store_info"]["longitude"]
        hours = data[0]["store_info"]["hours"].split(";")[:-1]
        hours = [elem[2:].replace(",", " - ").replace("00", ":00") for elem in hours]
        days = [
            "Monday",
            "Tuesday",
            "Wednsday",
            "Thursday",
            "Friday",
            "Satarday",
            "Sunday",
        ]
        hours_of_operation = list(map(lambda day, hour: day + " " + hour, days, hours))
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
