import re
import csv
import json
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
    scraped_items = []

    DOMAIN = "rexall.ca"
    start_url = "https://api.rexall.ca/BeautyStoreLocatorExternalV3/Service.svc/StoreList?callback=jQuery112406116886901938874_1608282807022&APIKEY=supyYmaA3wywM700&Latitude=43.653226&Longitude=-79.3831843&NumResults=4000&ReturnRadius=6000&FilterAttributeList%5B0%5D%5BStoreAttribute.AttributeName%5D=Retail"

    response = session.get(start_url)
    data = re.findall(r"\((.+)\);", response.text)[0]
    data = json.loads(data)

    for poi in data["Store"]:
        store_url = "<MISSING>"
        location_name = poi["StoreName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["Province"]
        state = state if state else "<MISSING>"
        zip_code = poi["PostalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["StoreNumber"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["PhoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        hoo_dict = {}
        for key, hour in poi["RxHours"].items():
            if "Close" in key:
                day = key.replace("Close", "")
                if hour:
                    if hoo_dict.get(day):
                        hoo_dict[day]["closes"] = hour
                    else:
                        hoo_dict[day] = {}
                        hoo_dict[day]["closes"] = hour
                else:
                    hoo_dict[day] = {"opens": False}
            if "Open" in key:
                day = key.replace("Open", "")
                if hour:
                    if hoo_dict.get(day):
                        hoo_dict[day]["opens"] = hour
                    else:
                        hoo_dict[day] = {}
                        hoo_dict[day]["opens"] = hour
                else:
                    hoo_dict[day] = {"opens": False}
        for day, hours in hoo_dict.items():
            if hours["opens"]:
                opens = hours["opens"]
                closes = hours["closes"]
                hours_of_operation.append(f"{day} {opens} - {closes}")
            else:
                hours_of_operation.append(f"{day} closed")
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
