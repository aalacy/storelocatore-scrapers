import re
import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


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

    DOMAIN = "costcutter.co.uk"
    start_url = "https://www.costcutter.co.uk/location-finder/"

    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    all_locations = []
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=10,
        max_search_results=None,
    )
    for lat, lng in all_coords:
        formdata = {
            "location.lat": lat,
            "location.lon": lng,
            "postcode": "",
            "locality": "[object Object]",
            "entityType": "address",
            "point": "[object Object]",
        }
        response = session.post(start_url, data=formdata, headers=headers)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath("//div[@data-distance]")

    for poi_html in all_locations:
        store_url = poi_html.xpath(
            './/a[@class="button set-local-home green clear short"]/@href'
        )
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"

        location_name = poi_html.xpath(".//h3/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = ""
        if poi_html.xpath("@data-addressline1"):
            street_address = poi_html.xpath("@data-addressline1")[0]
        if poi_html.xpath("@data-addressline2") and street_address:
            street_address += ", " + poi_html.xpath("@data-addressline2")[0]
        else:
            street_address = poi_html.xpath("@data-addressline2")[0]
        if "CASTLEMILK" in street_address:
            loc_response = session.get(store_url)
            street_address = re.findall('storeAddress = "(.+?)";', loc_response.text)[
                0
            ].split(", ")[:2]
            street_address = ", ".join(street_address)
        city = poi_html.xpath("@data-town")
        city = city[0] if city else "<MISSING>"
        state = poi_html.xpath("@data-county")
        state = state[0] if state and state[0].strip() else "<MISSING>"
        zip_code = poi_html.xpath("@data-postcode")
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi_html.xpath(".//@data-storeid")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi_html.xpath('.//p[@class="tel"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi_html.xpath("@data-fasciatype")[0]
        latitude = poi_html.xpath("@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath("@data-lon")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = poi_html.xpath(
            './/div[@class="span4 opening-hours"]/div//p//text()'
        )
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
