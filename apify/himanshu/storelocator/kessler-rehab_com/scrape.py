import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.kessler-rehab.com//sxa/search/results/?s={75078478-6727-4E71-8FC2-BED8FAD1B00B}&itemid={AF08CF64-F629-40A6-81AA-0B56D5A0185A}&sig=locations-cards&o=Title%2CAscending&p=20&v=%7BDD817789-9335-4441-B604-DC2901221E22%7D"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)

    for poi in data["Results"]:
        poi_html = etree.HTML(poi["Html"])
        store_url = poi_html.xpath('//a[contains(text(), "View location")]/@href')[0]
        store_url = urljoin(start_url, store_url)
        location_name = poi_html.xpath('//h3[@class="loc-result-card-name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath(
            '//div[@class="loc-result-card-address-container"]/div/text()'
        )
        street_address = raw_address[0].strip()
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(
            '//div[@class="loc-result-card-phone-container"]//a/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = poi_html.xpath("//@data-latlong")[0].split("|")
        latitude = geo[0]
        longitude = geo[1]
        hoo = poi_html.xpath(
            '//div[@class="mobile-container field-businesshours"]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
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
