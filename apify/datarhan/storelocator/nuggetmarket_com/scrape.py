import csv
from lxml import etree
from urllib.parse import urljoin

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

    DOMAIN = "nuggetmarket.com"
    start_url = "https://www.nuggetmarket.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//li[@itemscope]")
    for poi_html in all_locations:
        poi_url = poi_html.xpath("./a/@href")[0]
        poi_url = urljoin(start_url, poi_url)
        loc_response = session.get(poi_url)
        loc_dom = etree.HTML(loc_response.text)

        poi_name = poi_html.xpath('.//a[@itemprop="name"]/text()')
        poi_name = poi_name[0] if poi_name else "<MISSING>"
        street = poi_html.xpath('.//dd[@itemprop="streetAddress"]/text()')
        street = street[0] if street else "<MISSING>"
        city = poi_html.xpath('.//span[@itemprop="addressLocality"]/text()')[0].split(
            ", "
        )[0]
        state = (
            poi_html.xpath('.//span[@itemprop="addressLocality"]/text()')[0]
            .split(", ")[-1]
            .split()[0]
        )
        zip_code = poi_html.xpath('.//span[@itemprop="postalCode"]/text()')[0]
        country_code = "<MISSING>"
        poi_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        poi_type = "<MISSING>"
        if "Fork Lift" in poi_name:
            poi_type = "Fork Lift"
        elif "Sonoma" in poi_name:
            poi_type = "Sonoma"
        elif "Food 4 Less" in poi_name:
            poi_type = "Food 4 Less"
        elif "Corporate Office" in poi_name:
            continue
        else:
            poi_type = "Nugget"
        geo = (
            loc_dom.xpath('//a[contains(@href, "/@")]/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )
        latitude = geo[0]
        longitude = geo[1]
        hoo = loc_dom.xpath('//dd[@itemprop="openingHours"]/text()')
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
