import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "eatgarbanzo.com"
    start_url = "https://eatgarbanzo.com/wp-admin/admin-ajax.php"

    formdata = {
        "address": "",
        "formdata": "nameSearch=&addressInput=&addressInputCity=&addressInputState=&addressInputCountry=&tag_to_search_for=&ignore_radius=0",
        "lat": "39.7392358",
        "lng": "-104.990251",
        "name": "",
        "radius": "1000",
        "tags": "",
        "action": "csl_ajax_onload",
    }

    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.post(start_url, headers=headers, data=formdata)
    data = json.loads(response.text)

    for poi in data["response"]:
        if "CLOSED" in poi["name"]:
            continue
        store_url = poi["url"]
        store_url = store_url if store_url else "<MISSING>"
        street_address = poi["address"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        street_address = parse_address_intl(street_address).street_address_1
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["data"]["sl_country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["data"]["sl_id"]
        location_name = poi["name"]
        phone = poi["data"]["sl_phone"]
        phone = phone if phone else "<MISSING>"
        if "http" in phone:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["data"]["sl_latitude"]
        longitude = poi["data"]["sl_longitude"]
        hoo = etree.HTML(poi["data"]["sl_hours"])
        if hoo:
            hoo = [
                " ".join([e.strip() for e in elem.split()])
                for elem in hoo.xpath("//text()")
                if elem.strip()
            ]
        hours_of_operation = (
            " ".join(hoo).strip().split(" Online")[0].replace("Opens on 1.4.21 ", "")
            if hoo
            else "<MISSING>"
        )
        if hours_of_operation == "CLOSED":
            continue

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
