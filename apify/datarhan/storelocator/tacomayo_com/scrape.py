import re
import csv
from time import sleep
from lxml import etree
import demjson

from sgrequests import SgRequests
from sgselenium import SgFirefox


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

    DOMAIN = "tacomayo.com"
    start_url = "http://tacomayo.com/locations.aspx#.YAa2opNKgWq"
    response = session.get(start_url)

    with SgFirefox() as driver:
        driver.get("http://tacomayo.com/locations.aspx#.YAa2opNKgWq")
        driver.find_element_by_id("map_radius").click()
        driver.find_element_by_xpath('//option[@value="0"]').click()
        driver.find_element_by_id("map_address_button").click()
        sleep(2)
        dom = etree.HTML(driver.page_source)
    all_locations = dom.xpath('//tr[@class="map_locationsTableRow"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//td[@class="locations_phone"]//a/@href')
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath(".//h3/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath(
            './/td[@class="map_locationsTableAddress"]/p/text()'
        )
        street_address = raw_address[0]
        street_address = (
            street_address[:-1] if street_address.endswith(",") else street_address
        )
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = poi_html.xpath("@id")[0][1:]
        location_type = poi_html.xpath('.//td[@class="locations_store"]/text()')
        location_type = location_type[0] if location_type else "<MISSING>"
        poi = re.findall(
            r's%s" ?:(.+?),* ?"s\d+?"' % store_number, response.text.replace("\n", "")
        )
        if not poi:
            poi = poi = re.findall(
                r's%s" ?:(.+?);' % store_number, response.text.replace("\n", "")
            )
        poi = poi[0]
        poi = demjson.decode(
            poi.strip()[:-1].replace("new google.maps.LatLng(", '"').replace("),", '",')
        )

        phone = "<MISSING>"
        latitude = poi["point"].split(",")[0]
        longitude = poi["point"].split(",")[-1]
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
