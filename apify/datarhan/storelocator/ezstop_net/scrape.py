import re
import csv
import demjson
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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "ezstop.net"
    start_url = "https://ezstop.net/EZMap.aspx"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    geo_data = dom.xpath('//script[contains(text(), "markers")]/text()')[0]
    geo_data = re.findall("markers = (.+?);", geo_data.replace("\n", ""))[0]
    all_geo = demjson.decode(geo_data)

    all_locations = dom.xpath('//table[@id="ContentPlaceHolder_center_DLLocations"]/tr')
    next_page = dom.xpath('//input[@value="Next >"]')
    page = 1
    while next_page:
        url = f"https://ezstop.net/EZMap.aspx?Page={str(page)}"
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//table[@id="ContentPlaceHolder_center_DLLocations"]/tr'
        )

        geo_data = dom.xpath('//script[contains(text(), "markers")]/text()')[0]
        geo_data = re.findall("markers = (.+?);", geo_data.replace("\n", ""))[0]
        all_geo += demjson.decode(geo_data)

        next_page = dom.xpath('//input[@value="Next >"]')
        page += 1

    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath(".//b/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath("./td/text()")
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if not raw_address:
            continue
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = location_name.split()[-1]
        phone = raw_address[-1]
        location_type = "<MISSING>"
        geo = [elem for elem in all_geo if elem["description"] == street_address][0]
        latitude = geo["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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
