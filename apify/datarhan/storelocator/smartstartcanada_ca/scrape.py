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

    start_url = "https://www.smartstartcanada.ca/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath(
        '//div[@id="cssmenu"]//a[contains(text(), "Locations")]/following-sibling::ul//a/@href'
    )[:-1]
    for url in all_states:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath(
            '//li/strong/a[contains(text(), "Smart Start")]/@href'
        )

        for store_url in all_locations:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            raw_data = loc_dom.xpath('//ul[@id="locationInfo"]/li/text()')
            if len(raw_data) == 5:
                raw_data = [" ".join(raw_data[:2])] + raw_data[2:]
            if "Bay C" in raw_data[1]:
                raw_data = [" ".join(raw_data[:2])] + raw_data[2:]
            location_name = loc_dom.xpath('//div[@id="panel3_list"]/h3/text()')
            location_name = location_name[0] if location_name else "<MISSING>"
            street_address = raw_data[0]
            city = raw_data[1].split(", ")[0]
            state = raw_data[1].split(", ")[-1].split()[0]
            zip_code = " ".join(raw_data[1].split(", ")[-1].split()[1:])
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = raw_data[2].split(":")[-1].strip()
            location_type = "<MISSING>"
            latitude = "<INACCESSIBLE>"
            longitude = "<INACCESSIBLE>"
            hours_of_operation = "<MISSING>"
            if len(raw_data) > 3:
                hours_of_operation = raw_data[-1].split("Operation: ")[-1]

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
