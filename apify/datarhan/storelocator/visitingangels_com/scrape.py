import csv
from urllib.parse import urljoin
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
    scraped_items = []

    DOMAIN = "visitingangels.com"
    start_url = "https://www.visitingangels.com/senior-home-care-{}-{}"

    response = session.get("https://www.visitingangels.com/office-locator")
    dom = etree.HTML(response.text)
    us_state_abbrev = {}
    for state_html in dom.xpath('//select[@id="StateCode"]/option')[1:]:
        state_name = state_html.xpath("text()")[0]
        state_abr = state_html.xpath("@value")[0]
        us_state_abbrev[state_name] = state_abr

    all_locations = []
    for state, abr in us_state_abbrev.items():
        response = session.get(start_url.format(state.replace(" ", "-"), abr))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="franInfo"]')

    for poi_html in all_locations:
        store_url = urljoin(start_url, poi_html.xpath(".//a/@href")[0])
        location_name = poi_html.xpath("text()")[0].strip()
        street_address = poi_html.xpath("text()")[2].strip()
        city = poi_html.xpath("text()")[3].split()[:-2]
        city = " ".join(city).strip() if city else "<MISSING>"
        state = poi_html.xpath("text()")[3].split()[-2].strip()
        zip_code = poi_html.xpath("text()")[3].split()[-1].strip()
        country_code = "<MISSING>"
        store_number = store_url.split("_")[-1]

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        phone = loc_dom.xpath('//div[@class="fran-info"]/text()')
        phone = phone[-1] if phone else "<MISSING>"
        phone = (
            phone.split()[0]
            if len(phone.split()[0]) > 10
            else " ".join(phone.split()[:2])
        )
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
