import re
import csv
import json
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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

    DOMAIN = "aureliospizza.com"
    start_url = "https://www.aureliospizza.com/wp-admin/admin-ajax.php?action=get_store_data&yourstoreSlug=undefined%2Caddison%2Cbourbonnais%2Ccedar-lake%2Cchicago-heights%2Cchicago-south-loop%2Ccrete%2Ccrown-point%2Cdowners-grove%2Cfishers%2Cfrankfort%2Cgeneva%2Cgriffith%2Chammond%2Chomewood%2Cjoliet%2Clagrange%2Claporte%2Clas-vegas-north%2Clowell%2Cmokena%2Cmorris%2Cmunster%2Cnaperville-springbrook%2Cnaples%2Cnew-lenox%2Cpalos-heights%2Cplainfield%2Cportage%2Cramsey-minnesota%2Crichton-park%2Cschererville%2Csouth-holland%2Ctinley-park%2Cvalparaiso%2Coakbrook%2Cwheaton-winfield-il%2Cwinfield-in-lakes-of-the-four-seasons%2Cwoodridge&nonce=be5eeab2f8"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data[1:]:
        store_url = poi["url"]
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath('//script[@id="FullPageMapScript-js-extra"]/text()')[0]
        data = re.findall("ScriptParams =(.+?);", data)[0]
        data = json.loads(data)
        data = json.loads(data["location"])

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@id="MapAddress"]/p/text()')
        if len(raw_address) != 1:
            raw_address = [elem.strip() for elem in raw_address]
            street_address = raw_address[0]
            street_address = street_address if street_address else "<MISSING>"
            city = raw_address[1]
            state = loc_dom.xpath('//div[@class="location"]/a/text()')[1].split()[-2]
            zip_code = raw_address[-2]
            country_code = raw_address[-1]
        else:
            raw_address = raw_address[0].split(", ")
            street_address = raw_address[0]
            street_address = street_address if street_address else "<MISSING>"
            city = raw_address[1]
            state = loc_dom.xpath('//div[@class="location"]/a/text()')[1].split()[-2]
            zip_code = raw_address[-1].split()[-1]
            country_code = "<MISSING>"
        store_number = poi["storeID"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        location_type = location_type if location_type else "<MISSING>"
        latitude = data["latitude"]
        longitude = data["longitude"]
        hours_of_operation = loc_dom.xpath(
            '//h5[contains(text(), "Hours")]/following-sibling::p[1]/text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
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
