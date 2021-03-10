import csv
import json
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

    DOMAIN = "inshape.com"
    start_url = "https://www.inshape.com/catalog/category/view/id/3/?no_cache=true&p={}"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    formdata = {"itoris_layerednavigation": "true"}

    all_locations = []
    for i in range(1, 6):
        response = session.post(
            start_url.format(str(i)), data=formdata, headers=headers
        )
        data = json.loads(response.text)
        dom = etree.HTML(data["content_html"])
        all_locations += dom.xpath('//a[span[contains(text(), "Club page")]]/@href')

    for url in all_locations:
        poi_url = urljoin(start_url, url)
        loc_response = session.get(poi_url)
        loc_dom = etree.HTML(loc_response.text)

        poi_name = loc_dom.xpath('//h1[@class="title"]/text()')
        poi_name = poi_name[0] if poi_name else "<MISSING>"
        street = loc_dom.xpath('//p[@itemprop="street-address"]/text()')
        street = street[0] if street else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="locality"]/text()')
        city = city[0].replace(",", "").strip() if city else "<MISSING>"
        state = loc_dom.xpath('//span[@itemprop="postal-code"]/text()')[0].split()[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postal-code"]/text()')[0].split()[
            -1
        ]
        country_code = "<MISSING>"
        poi_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        poi_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours = loc_dom.xpath('//div[@class="tab-content"]//table//text()')
        hours = [elem for elem in hours if "pm" in elem]
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hoo = " ".join(list(map(lambda day, hour: day + " " + hour, days, hours)))

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
