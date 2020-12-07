import csv
import json
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
    session = SgRequests()

    items = []

    DOMAIN = "atriumhealth.org"
    start_url = "https://atriumhealth.org/mobileDataApI/MobileserviceAPi/LocationSearch?cityName=&locationType=All+Locations&community=All+Communities&locationName=&pageNumber=2&pageSize=5&sortBy=&childrensLocationOnly=false&latitude=35.2270869&longitude=-80.8431267"

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Connection": "keep-alive",
        "Host": "atriumhealth.org",
        "Referer": "https://atriumhealth.org/locations?cityName=&locationType=All_Locations&community=All_Communities&locationName=&pageNumber=1&pageSize=5&sortBy=&childrensLocationOnly=false&latitude=35.2270869&longitude=-80.8431267&datasource=f829e711-f2ef-4b46-98d6-a268f958a2d0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    }

    all_poi = []
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)
    all_poi += data["Locations"]

    total_poi_site = data["Summary"]["totalCount"]
    total_pages = total_poi_site // 5 + 2
    for page in range(2, total_pages):
        page_response = session.get(
            add_or_replace_parameter(start_url, "pageNumber", str(page)),
            headers=headers,
        )
        page_data = json.loads(page_response.text)
        all_poi += page_data["Locations"]

    for poi in all_poi:
        store_url = "https://atriumhealth.org" + poi["ClickableUri"]
        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["PostalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["LocationTypeValue"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["HoursAdditionalDetails"]
        hours_of_operation = (
            hours_of_operation.replace("<br/>", "")
            if hours_of_operation
            else "<MISSING>"
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
