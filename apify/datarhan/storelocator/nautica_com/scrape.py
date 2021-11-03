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
    scraped_items = []

    DOMAIN = "nautica.com"
    start_url = "https://www.nautica.com/on/demandware.store/Sites-nau-Site/default/Stores-GetNearestStores?state=&countryCode={}&onlyCountry=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get(
        "https://www.nautica.com/on/demandware.store/Sites-nau-Site/default/Stores-AllStores"
    )
    dom = etree.HTML(response.text)
    all_urls = dom.xpath('//div[@class="listname"]/a/@href')
    all_contry_codes = [
        e.split("LocName=")[-1].split("%2")[0] for e in all_urls if "LocName=" in e
    ]
    all_contry_codes = list(set(all_contry_codes))

    for country_code in all_contry_codes:
        response = session.get(start_url.format(country_code), headers=headers)
        data = json.loads(response.text)

        for poi in data.values():
            store_url = "https://www.nautica.com/store-details?storeid={}".format(
                poi["storeID"]
            )
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += ", " + poi["address2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["stateCode"]
            state = state if state else "<MISSING>"
            zip_code = poi["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["countryCode"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["storeID"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["phone"]
            phone = phone.split("<")[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = etree.HTML(poi["storeHours"])
            if hours_of_operation:
                hours_of_operation = hours_of_operation.xpath("//text()")[1:]
                hours_of_operation = [
                    elem.strip() for elem in hours_of_operation if elem.strip()
                ]
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
            check = f"{location_name} {street_address}"
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
