import csv
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

    DOMAIN = "imagesun.com"
    start_url = "http://imagesun.com/tanning.shtml"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    all_locations = []
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//select[@name="menu1"]/option/@value')[1:]
    more_url = [url for url in all_locations if "_locations" in url]
    for url in more_url:
        response = session.get(url, headers=headers)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[@class="subhead"]/@href')

    for poi_url in list(set(all_locations)):
        if poi_url == "http://www.imagesun.com/salon_location.shtml":
            continue
        if poi_url in more_url:
            continue
        response = session.get(poi_url, headers=headers)
        dom = etree.HTML(response.text)

        poi_name = dom.xpath('//span[@class="h1"]/text()')
        poi_name = poi_name[0] if poi_name else "<MISSING>"
        address_raw = dom.xpath(
            '//span[@class="subhead"]/span[@class="content"]/text()'
        )
        if len(address_raw) > 4:
            address_raw = address_raw[:4]
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if "Across from K-Mart" in address_raw[2]:
            address_raw = address_raw[:2] + address_raw[3:]
        if "East of Van Dyke" in address_raw[2]:
            address_raw = address_raw[:2] + address_raw[3:]
        if len(address_raw) == 4:
            address_raw = [", ".join(address_raw[:2])] + address_raw[2:]
        street = address_raw[0]
        city = address_raw[1].split(", ")[0]
        state = address_raw[1].split(", ")[-1].split()[0]
        zip_code = address_raw[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        poi_number = "<MISSING>"
        phone = address_raw[-1].split("(")[0].strip()
        poi_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "&ll=" in dom.xpath('//a[@class="mainnav"]/@href')[0]:
            geo = (
                dom.xpath('//a[@class="mainnav"]/@href')[0]
                .split("&ll=")[-1]
                .split("&")[0]
                .split(",")
            )
            latitude = geo[0]
            longitude = geo[1]
        hoo = "<MISSING>"

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
