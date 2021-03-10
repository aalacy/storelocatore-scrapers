import csv
import demjson
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

    DOMAIN = "pharmaprix.ca"
    start_url = "https://stores.pharmaprix.ca/en/province/qc/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.post(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_poi = dom.xpath('//div[@class="col-sm-6 col-md-3 listing-link"]/a/@href')
    for store_url in all_poi:
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        poi = store_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "streetAddress")]/text()'
        )
        poi = demjson.decode(poi[0])

        location_name = poi["name"]
        location_name = (
            location_name.replace("&#39;", "'")
            .replace("&amp;", "")
            .replace("&#233;", "")
            if location_name
            else "<MISSING>"
        )
        street_address = poi["address"]["streetAddress"]
        street_address = (
            street_address.replace("&#39;", "'") if street_address else "<MISSING>"
        )
        city = poi["address"]["addressLocality"]
        city = (
            city.replace("&#39;", "'").replace("&amp;", " ").replace("&#233;", " ")
            if city
            else "<MISSING>"
        )
        state = poi["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = store_dom.xpath('//a[@class="locator-result__directions"]/@href')[
            0
        ].split("+")[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = store_url.split("/")[-2]
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = store_dom.xpath("//div/@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = store_dom.xpath("//div/@data-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = poi["openingHours"]
        hours_of_operation = [elem for elem in hours_of_operation if type(elem) == str]
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        if hours_of_operation == "Mo, Tu, We, Th, Fr, Sa, Su":
            hours_of_operation = "Open 24 Hours"

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
