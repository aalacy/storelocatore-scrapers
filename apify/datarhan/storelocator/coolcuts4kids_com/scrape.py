import re
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
    scraped_items = []

    DOMAIN = "coolcuts4kids.com"
    start_url = "http://www.coolcuts4kids.com/salonlocatorbrowse/default.asp?state=&city=&selOpt=5&sd=-1"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//div[@id="result_StateList"]/ul/li/@onclick')
    for url in all_states:
        state_url = (
            "http://www.coolcuts4kids.com/salonlocatorbrowse/"
            + url.split("='")[-1].split("'")[0]
        )
        response = session.get(state_url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@id="result_StateCitySearch"]/ul/li')
        all_cities = dom.xpath('//div[@id="result_CityList"]/ul/li/@onclick')
        for url in all_cities:
            state_url = (
                "http://www.coolcuts4kids.com/salonlocatorbrowse/"
                + url.split("='")[-1].split("'")[0]
            )
            response = session.get(state_url)
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//div[@id="result_StateCitySearch"]/ul/li')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//div[@class="result_MoreInfo"]/a/@href')
        store_url = urljoin(start_url, store_url[0])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@id="detailA_Salon"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@class="result_Street"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//div[@class="result_Location"]/text()')[0].split(", ")[
            0
        ]
        state = (
            poi_html.xpath('.//div[@class="result_Location"]/text()')[0]
            .split(", ")[-1]
            .split()[0]
        )
        zip_code = (
            poi_html.xpath('.//div[@class="result_Location"]/text()')[0]
            .split(", ")[-1]
            .split()[-1]
        )
        country_code = "<MISSING>"
        store_number = store_url.split("=")[-1]
        phone = poi_html.xpath('.//div[@class="result_Phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall('latitude":"(.+?)",', loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall('longitude":"(.+?)",', loc_response.text)
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//div[@id="detailC"]/p/text()')
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
