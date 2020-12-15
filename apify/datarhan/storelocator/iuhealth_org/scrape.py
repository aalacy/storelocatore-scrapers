import csv
import json
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "iuhealth.org"
    start_url = "https://4ihkkbfuuk-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.3.1)%3B%20Browser%20(lite)%3B%20JS%20Helper%20(3.2.1)%3B%20react%20(16.8.6)%3B%20react-instantsearch%20(6.7.0)&x-algolia-api-key=cc321cac4dc07696439db06c6a06144b&x-algolia-application-id=4IHKKBFUUK"
    body = '{"requests":[{"indexName":"locations","params":"highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&maxValuesPerFacet=5000&query=&hitsPerPage=1200&getRankingInfo=true&aroundLatLng=&aroundRadius=all&filters=type%3Alocation%20OR%20type%3Ahospital&clickAnalytics=true&analyticsTags=findLocationPage&page=0&facets=%5B%22address.city%22%2C%22facilityType%22%2C%22umbrellaServices%22%5D&tagFilters="}]}'
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data["results"][0]["hits"]:
        store_url = "https://iuhealth.org/find-locations/" + poi["slug"]
        location_name = poi["name"]
        location_name = location_name.strip() if location_name else "<MISSING>"
        street_address = poi["address"]["address1"]
        if poi["address"]["address2"]:
            street_address += " " + poi["address"]["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city.strip() if city else "<MISSING>"
        state = poi["address"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["entryID"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["facilityType"]
        latitude = poi["_geoloc"]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["_geoloc"]["lng"]
        longitude = longitude if longitude else "<MISSING>"

        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        hours_of_operation = store_dom.xpath(
            '//table[@class="LocationCardText__hours"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        if not hours_of_operation:
            hours_of_operation = store_dom.xpath(
                '//p[@class="LocationCardText__todays-hours"]//text()'
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
