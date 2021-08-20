import csv
import json
from lxml import etree
from urllib.parse import urljoin

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

    DOMAIN = "europcar.co.uk"
    start_url = "https://www.europcar.co.uk/en_GB/contents/worldwide/WESTEUR/GB/car.stations.json"

    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)

    for poi in data:
        store_url = urljoin(start_url, poi["url"])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        data = (
            loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
            .replace("\n", "")
            .replace("\t", "")
        )
        data = json.loads(data.replace('}{"@type": "Opening', '}, {"@type": "Opening'))

        location_name = poi["name"]
        street_address = " ".join(poi["address"]["streetLines"])
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["address"]["postCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country"]
        if country_code != "United Kingdom":
            continue
        store_number = "<MISSING>"
        phone = data["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        days = loc_dom.xpath('//div[@class="colDay"]/span/text()')
        hours = []
        for elem in loc_dom.xpath('//div[contains(@class, "colNormalHours")]')[1:]:
            h = elem.xpath('.//div[@class="plageHour"]/text()')
            if h:
                h = " ".join([e for e in h[0].strip().split()])
            else:
                h = " "
            hours.append(h)
        hoo = list(map(lambda d, h: d + " " + h, days, hours))
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
