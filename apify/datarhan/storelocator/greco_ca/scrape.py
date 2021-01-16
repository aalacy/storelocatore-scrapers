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
    scraped_items = []

    DOMAIN = "greco.ca"
    start_url = "https://greco.ca/location-results/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    states = dom.xpath('//select[@name="city_term_id"]/optgroup')
    for state_html in states:
        state = state_html.xpath("@label")[0]
        cities = state_html.xpath(".//option/@value")
        for city_id in cities:
            city_url = "https://greco.ca/location-results/?city_term_id={}".format(
                city_id
            )
            response = session.get(city_url)
            dom = etree.HTML(response.text)
            all_locations = dom.xpath('//table[@class="location-info"]/tbody/tr')

            for poi_html in all_locations:
                store_url = "<MISSING>"
                raw_address = poi_html.xpath(".//td/text()")
                raw_address = [elem.strip() for elem in raw_address if elem.strip()]
                location_name = raw_address[0]
                street_address = raw_address[2]
                location_type = "<MISSING>"
                city = raw_address[1]
                zip_code = "<MISSING>"
                country_code = "<MISSING>"
                store_number = "<MISSING>"
                phone = poi_html.xpath(".//td/a/text()")
                phone = phone[0] if phone else "<MISSING>"
                if "menu" in phone.lower():
                    phone = "<MISSING>"
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
                check = f"{location_name} {street_address}"
                if check not in scraped_items:
                    scraped_items.append(check)
                    items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
