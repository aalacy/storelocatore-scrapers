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

    start_url = "https://www.sturdyonline.com/Locations.aspx"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="content1"]/table[2]//tr/td')
    all_locations += dom.xpath('//td[h2[contains(text(), "Wildwood Crest")]]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//h2/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = poi_html.xpath(".//text()")
        raw_data = [e.strip() for e in raw_data if e.strip() and "P.O" not in e][1:3]
        if not raw_data:
            continue
        street_address = raw_data[0]
        street_address = street_address if street_address else "<MISSING>"
        city = raw_data[1].split(", ")[0]
        state = raw_data[1].split(", ")[-1].split()[0]
        zip_code = raw_data[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//p[strong[contains(text(), "Voice:")]]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        days = dom.xpath('//table[@height="206"]//tr/td[1]/p/text()')[:4]
        hours = dom.xpath('//table[@height="206"]//tr/td[3]/p/text()')[:4]
        hoo = list(map(lambda d, h: d + " " + h, days, hours))
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        if location_name == "Wildwood Crest":
            hours_of_operation = " ".join(
                dom.xpath(
                    '//tr[td[h3[contains(text(), "Hours")]]]/following-sibling::tr/td//text()'
                )
            )

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
