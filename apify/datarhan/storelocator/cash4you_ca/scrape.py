import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://cash4you.ca/company/find-a-store/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.post(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//a[contains(@href, "city")]/@href')
    for store_url in all_cities:
        response = session.get(store_url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//section[@class="store_dtl_sec"]/div')[1:]

        for poi_html in all_locations:
            location_name = "<MISSING>"
            raw_address = poi_html.xpath(
                './/div[@class="store_title text-center"]/h3/text()'
            )[0].split(", ")
            if len(raw_address) == 5:
                raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
            street_address = raw_address[0]
            city = raw_address[1]
            state = raw_address[2]
            zip_code = raw_address[3]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath(
                './/label[contains(text(), "Phone:")]/following-sibling::span/text()'
            )
            phone = phone[0].strip() if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hoo = poi_html.xpath('.//div[h4[contains(text(), "Store Hours:")]]//text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo[1:-4]) if hoo else "<MISSING>"

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
