import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


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

    DOMAIN = "mcmworldwide.com"
    start_url = "https://us.mcmworldwide.com/on/demandware.store/Sites-MCM-US-Site/en_US/Stores-FindbyNumberOfStores?format=ajax&noOfStores=10.00&searchType=findbyGeoLocation&searchKey=toronto&showOnlyMcmBoutiquesFlag=false&lat={}&lng={}&source=undefined"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=200
    )
    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//div[@class="mod_accordion js-checkout-storeresult"]/div'
        )

    for poi_html in all_locations:
        location_name = poi_html.xpath('.//span[@class="store-name txt-mono"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//p[@class="store-address"]/span/text()')
        addr = parse_address_usa(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        if len(state) > 2:
            continue
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        if country_code not in ["US", "United States"]:
            continue
        store_number = poi_html.xpath("@data-store-id")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi_html.xpath('.//a[@class="store-phone"]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath("@data-lng")
        longitude = longitude if longitude else "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="store-hours"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        store_url = "https://us.mcmworldwide.com/en_US/stores/{}/{}".format(
            location_name.lower().replace(" ", "-"), store_number
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
