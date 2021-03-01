import re
import csv
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


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

    DOMAIN = "hss.com"
    start_url = (
        "https://www.hss.com/hire/find-a-branch?latitude=&longitude=&brands=hire&q={}"
    )

    all_locations = []
    all_coords = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=50,
        max_search_results=None,
    )
    for code in all_coords:
        response = session.get(start_url.format(code))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//form[@name="pos_details_form"]/@action')

    for url in list(set(all_locations)):
        poi_url = "https://www.hss.com" + url
        loc_response = session.get(poi_url)
        loc_dom = etree.HTML(loc_response.text)

        poi_name = re.findall('storename = "(.+)";', loc_response.text)
        if not poi_name:
            continue
        poi_name = poi_name[0]
        street = re.findall('storeaddressline1 = "(.+?)";', loc_response.text)[0]
        street_2 = re.findall('storeaddressline2 = "(.+?)";', loc_response.text)
        if street_2:
            street += " " + street_2[0]
        city = re.findall('storeaddresstown = "(.+?)";', loc_response.text)
        city = city[0] if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = re.findall('storeaddresspostalCode = "(.+?)";', loc_response.text)
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = re.findall(
            'storeaddresscountryname = "(.+?)";', loc_response.text
        )
        country_code = country_code[0] if country_code else "<MISSING>"
        poi_number = "<MISSING>"
        phone = re.findall('storeaddressphone = "(.+?)";', loc_response.text)
        phone = phone[0] if phone else "<MISSING>"
        poi_type = "<MISSING>"
        latitude = re.findall("latitude = (.+?);", loc_response.text)[0]
        longitude = re.findall("longitude = (.+?);", loc_response.text)[0]
        hoo = loc_dom.xpath('//div[@class="store-openings weekday_openings"]//text()')
        hoo = [
            elem.strip().replace("\t", "").replace("\n", " ")
            for elem in hoo
            if elem.strip()
        ]
        hoo = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            DOMAIN,
            poi_url,
            poi_name,
            street,
            city,
            state,
            zip_code,
            country_code,
            poi_number,
            phone,
            poi_type,
            latitude,
            longitude,
            hoo,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
