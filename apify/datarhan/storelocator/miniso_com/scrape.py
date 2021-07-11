import re
import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    start_url = "https://www.miniso.com/EN/map"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_countries = dom.xpath('//select[@id="chkcountry"]/option')
    for country in all_countries:
        code = country.xpath("@value")[0]
        country_code = country.xpath(".//text()")[0]
        url = "https://www.miniso.com/EN/map/GetStoreList"
        frm = {
            "chkcountry": code,
            "chkarea": "",
            "k": "",
            "pageindex": "1",
            "pagesize": "500",
        }
        all_locations = session.post(url, data=frm).json()

        for poi in all_locations:
            print(len(poi["LinkAddr"].split(",")), poi["LinkAddr"])

            store_url = start_url
            location_name = poi["StoreName"]
            location_name = location_name if location_name else "<MISSING>"
            addr = parse_address_intl(poi["LinkAddr"])
            street_address = addr.street_address_1
            if addr.street_address_2 and street_address:
                street_address += " " + addr.street_address_2
            elif not street_address and addr.street_address_2:
                street_address = addr.street_address_2
            if not street_address:
                street_address = poi["LinkAddr"].split(", ")[0]
            if not street_address.strip():
                continue
            street_address = street_address.replace("<*B1-143/144/145>", "")
            city = addr.city
            city = city if city else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"

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
