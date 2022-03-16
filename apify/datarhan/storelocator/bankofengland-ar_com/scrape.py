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

    start_url = "https://www.bankofengland-ar.com/connect/branch-info"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="body content"]//h3[contains(@id, "mcetoc_")]'
    )
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath("text()")
        location_name = location_name[0].strip() if location_name else "<MISSING>"

        if "Carlisle Banking Center" in location_name:
            raw_address = ["101 E Park St", "Carlisle, AR 72024"]
        elif "Scott Banking Center" in location_name:
            raw_address = ["11044 HWY 165 / PO Box 160", "North Little Rock, AR 72117"]
        elif "Riverdale Branch" in location_name:
            raw_address = ["1320 Rebsamen Park Rd", "Little Rock, AR 72202"]
        else:
            raw_address = poi_html.xpath(
                './/following-sibling::div[span[div[em[strong[contains(text(), "ADDRESS")]]]]]/span/div/text()'
            )
            if raw_address:
                raw_address = raw_address[:2]
            if not raw_address:
                raw_address = [
                    dom.xpath(
                        '//div[h3[contains(text(), "{}")]]/following-sibling::div[1]/span/div[1]/text()'.format(
                            location_name
                        )
                    )[-1].strip()
                ]
                raw_address += dom.xpath(
                    '//div[h3[contains(text(), "{}")]]/following-sibling::div[1]/span/div[2]/text()'.format(
                        location_name
                    )
                )
        street_address = raw_address[0]
        city = raw_address[1].split(",")[0].strip()
        state = raw_address[1].split(",")[-1].split()[0].strip()
        zip_code = raw_address[1].split(",")[-1].split()[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = (
            poi_html.xpath(".//following-sibling::div[1]/text()")[0]
            .split("Fax")[0]
            .split(":")[-1]
            .strip()
        )
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath(
            './/following-sibling::div[span[div[em[strong[contains(text(), "ADDRESS")]]]]]/span/div[em[strong[contains(text(),"LOBBY HOURS")]]]/following-sibling::div[1]//text()'
        )
        if hoo:
            hoo = hoo[0]
        if not hoo:
            hoo = dom.xpath(
                '//div[h3[contains(text(), "{}")]]/following-sibling::div[1]/span/div[div[em[strong[contains(text(), "LOBBY HOURS")]]]]/div[2]//text()'.format(
                    location_name
                )
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo)
        hours_of_operation = hoo.strip() if hoo else "<MISSING>"

        if location_name == "East Branch - England, AR":
            hours_of_operation = "Mon - Friday: 8:30 am - 4:30 pm"
        if location_name == "Carlisle Banking Center - Carlisle, AR":
            hours_of_operation = (
                "Mon - Thur: 8:30 am - 4:30 pm Friday: 8:30 am - 5:00 pm"
            )
        if location_name == "Scott Banking Center - North Little Rock, AR":
            hours_of_operation = "Mon - Friday: 8:00 am - 5:00 pm"
        if location_name == "Riverdale Branch - Little Rock, AR":
            hours_of_operation = "Mon - Friday: 8:30 am - 5:00 pm"

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
