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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "haggar.com"
    start_url = "https://www.haggar.com/storelisting?lang=default"

    response = session.get("https://www.haggar.com/stores/?lang=default")
    dom = etree.HTML(response.text)

    all_locations = []
    all_states = dom.xpath('//select[@id="dwfrm_storelocator_state"]/option/@value')[1:]
    for state in all_states:
        formdata = {
            "dwfrm_storelocator_state": state,
            "dwfrm_storelocator_findbystate": "Search",
        }
        response = session.post(start_url, data=formdata)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//table[@id="store-location-results"]/tbody/tr')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[@title="View Store Details"]/@href')
        store_url = (
            "https://www.haggar.com" + store_url[0] if store_url else "<MISSING>"
        )
        location_name = poi_html.xpath('.//div[@class="store-name"]/span/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//td[@class="store-address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if len(raw_address) == 4:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = raw_address[-1]
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//a[@class="phone-number"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('//div[@class="store-hours"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
