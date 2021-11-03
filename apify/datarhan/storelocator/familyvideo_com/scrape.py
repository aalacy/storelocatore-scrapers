import csv
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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

    DOMAIN = "familyvideo.com"

    start_url = (
        "http://apply.familyvideo.com/zip_locator.php?code={}&radius=200&more=no"
    )

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )
    all_locations = []
    for code in all_codes:
        response = session.get(start_url.format(code))
        dom = etree.HTML(response.text)
        all_poi = dom.xpath('//td[@class="zipLocationText"]/div[@id="sidebar"]//text()')
        all_poi = [elem.strip() for elem in all_poi if elem.strip()]
        poi = []
        for elem in all_poi:
            if "Map It" in elem:
                all_locations.append(poi)
                poi = []
                continue
            poi.append(elem)

    for poi in all_locations:
        store_url = "http://apply.familyvideo.com/zip_locator.php"
        location_name = "<MISSING>"
        street_address = " ".join(poi[0].split()[1:])
        city = poi[1].split(", ")[0]
        state = poi[1].split(", ")[-1].split()[0]
        zip_code = poi[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi[2]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = " ".join(poi[3:])

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
