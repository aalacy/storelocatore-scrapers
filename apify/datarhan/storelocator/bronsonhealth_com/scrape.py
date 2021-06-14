import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.bronsonhealth.com/api/locations/?fields=All&version=1&pageNumber=1&pageSize=10&sort=3&searchId=&criteria%5Bkeyword%5D=&criteria%5Bcity%5D=&criteria%5BstateCode%5D=&criteria%5BzipCode%5D="
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)
    all_locations = data["Values"]

    total_pages = data["TotalRecords"] // 10 + 2
    for page in range(2, total_pages):
        response = session.get(
            add_or_replace_parameter(start_url, "pageNumber", str(page)), headers=hdr
        )
        data = json.loads(response.text)
        all_locations += data["Values"]

    for poi in all_locations:
        store_url = urljoin("https://www.bronsonhealth.com/locations/", poi["Slug"])
        loc_reponse = session.get(store_url)
        loc_dom = etree.HTML(loc_reponse.text)

        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]["AddressLine1"]
        if poi["Address"]["AddressLine2"]:
            street_address += " " + poi["Address"]["AddressLine2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["Address"]["City"]
        city = city if city else "<MISSING>"
        state = poi["Address"]["StateAbbreviation"]
        state = state if state else "<MISSING>"
        zip_code = poi["Address"]["PostalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Address"]["Country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["LocationId"]
        phone = poi["PhoneNumbers"]["Main"]["WholeNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        if latitude == 0.0:
            latitude = "<MISSING>"
        longitude = poi["Longitude"]
        if longitude == 0.0:
            longitude = "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="OfficeHours"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        hoo = []
        if hours_of_operation == "<MISSING>":
            for day, hours in poi["OfficeHoursList"].items():
                if hours["Status"] == "Closed":
                    hoo.append(f"{day} - Closed")
                else:
                    opens = hours["OfficeHours"][0]["OpenTime"]
                    closes = hours["OfficeHours"][0]["CloseTime"]
                    hoo.append(f"{day} - {opens} - {closes}")
                    hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
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
