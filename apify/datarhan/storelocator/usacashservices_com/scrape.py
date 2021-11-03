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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = (
        "http://usacashservices.com/apps/Home.nsf/l_direct_lending_locations.xsp"
    )
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//a[contains(text(), "Locations")]/@href')
    all_locations = []
    for url in all_states:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations = re.findall(
            r'(http://www.usacashservices.com/APPS/Home.nsf/LocationInfo\?Openform.+?)",',
            response.text,
        )

        for url in all_locations:
            loc_response = session.get(url)
            loc_dom = etree.HTML(loc_response.text)

            raw_data = loc_dom.xpath("//div//text()")
            raw_data = [e.strip() for e in raw_data if e.strip() and e.strip() != ","]
            store_url = response.url
            location_name = "<MISSING>"
            street_address = raw_data[0]
            city = raw_data[1]
            state = raw_data[2]
            zip_code = raw_data[3]
            country_code = "<MISSING>"
            store_number = url.split("&")[-1]
            phone = raw_data[4]
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = " ".join(raw_data[-2:]).split("Business Hours: ")[-1]

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
