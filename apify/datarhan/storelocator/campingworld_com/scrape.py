import csv
import json
from lxml import etree
from urllib.parse import urljoin

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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "campingworld.com"
    start_url = "https://rv.campingworld.com/api/locationmiles?glcodes=RVA,082,FVA,HAN,TVA,AVA,MCG,AIR,HAR,NVA,BRI,APA,ROA,LAK,GNC,RAL,CFX,BUF,SYU,FAY,CNY,SRV,KIN,STA,CNC,002,MB,MNC&lat=39.04&lon=-77.48"

    response = session.get(start_url)
    all_locations = json.loads(response.text)

    for poi in all_locations:
        base_url = "https://rv.ganderoutdoors.com/dealer/"
        store_url = urljoin(base_url, poi["dealer_url"])
        location_name = poi["location_name__c"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["billing_street__c"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["billing_city__c"]
        city = city if city else "<MISSING>"
        state = poi["billing_state_code__c"]
        state = state if state else "<MISSING>"
        zip_code = poi["billing_postal_5code__c"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["billing_country_code__c"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["location_id__c"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone__c"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi["legal_name__c"]:
            if "Camping World" in poi["legal_name__c"]:
                location_type = "Camping World"
        latitude = poi["geolocation_latitude__c"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geolocation_longitude__c"]
        longitude = longitude if longitude else "<MISSING>"

        check = "{} {}".format(location_name, street_address)
        if check in scraped_items:
            continue
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        hoo = store_dom.xpath(
            '//div[@id="dealerHours"]/div[@class="storehours"]//div[@class="row hours-row"]//text()'
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

        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
