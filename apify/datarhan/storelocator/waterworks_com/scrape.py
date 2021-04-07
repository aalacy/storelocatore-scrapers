import csv
import json
from lxml import etree

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

    DOMAIN = "waterworks.com"
    start_url = "https://www.waterworks.com/us_en/storelocation/index/storelist/"

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    formdata = {"curPage": "1", "countryId": "US"}
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["storesjson"]:
        store_url = "https://www.waterworks.com/us_en/{}".format(
            poi["rewrite_request_path"]
        )
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["store_name"]
        street_address = poi["address"]
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zipcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country_id"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["storelocation_id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = loc_dom.xpath(
            '//dt[contains(text(), "Hours")]/following-sibling::dd//text()'
        )
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
