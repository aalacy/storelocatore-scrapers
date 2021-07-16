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
    scraped_items = []

    start_url = "https://www.xpresspa.com/Articles.asp?ID=262"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = []
    all_cities = dom.xpath(
        '//div[@id="div_articleid_262"]//h4[a[contains(@class, "link")]]'
    )
    for city_state in all_cities:
        city = city_state.xpath(".//a/text()")[0].split("-")[-1].strip().split(",")[0]
        if city in ["JFK", "LaGuardia"]:
            city = "New York"
        state = city_state.xpath(".//a/text()")[0].split("-")[0].strip()
        if state == "United Arab Emirates":
            state = "<MISSING>"
            country_code = "United Arab Emirates"

        all_locations = city_state.xpath(".//following-sibling::div[1]//ul/li")
        for poi_html in all_locations:
            store_url = start_url
            location_name = poi_html.xpath(".//a/b/text()")[0].strip()
            street_address = poi_html.xpath("text()")[0].strip()
            zip_code = "<MISSING>"
            country_code = "<MISSING>"
            if city == "Netherlands":
                city = "Amsterdam"
                state = "<MISSING>"
                country_code = "Netherlands"
            store_number = "<MISSING>"
            all_txt = poi_html.xpath(".//text()")
            phone = [e.strip() for e in all_txt if "Tel" in e]
            phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hoo = [e.strip() for e in all_txt if "Hours" in e]
            hours_of_operation = (
                hoo[0].split("Hours:")[-1].split("*")[0].strip() if hoo else "<MISSING>"
            )
            if city == "Amsterdam":
                country_code = "Netherlands"

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
            check = f"{location_name} {street_address} {city}"
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
