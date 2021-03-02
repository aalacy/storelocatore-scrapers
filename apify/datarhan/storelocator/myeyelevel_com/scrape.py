import csv
import json
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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "myeyelevel.com"
    start_url = "https://www.myeyelevel.com/US/customer/getCenterList.do"
    country_codes = ["0015", "0014"]
    for code in country_codes:
        formdata = {
            "pageName": "findCenter",
            "centerLati": "",
            "searchType": "",
            "centerLongi": "",
            "surDistance": "",
            "myLocLati": "0",
            "myLocLongi": "0",
            "countryCd": code,
            "cityCd": "",
            "centerName": "",
            "listSort": "D",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

        response = session.post(start_url, data=formdata, headers=headers)
        data = json.loads(response.text)

        for poi in data:
            if poi.get("homeurl"):
                store_url = "https://" + poi["homeurl"]
            else:
                store_url = "<MISSING>"
            if "www.myeyelevel.com" not in store_url:
                continue
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            raw_address = loc_dom.xpath(
                '//ul[@class="copyUl"]//span[@class="link"]/text()'
            )[0]
            structured_adr = parse_address_intl(raw_address)
            location_name = poi["centerName"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = structured_adr.street_address_1
            city = structured_adr.city
            if not city and len(raw_address.split(", ")) == 3:
                city = raw_address.split(", ")[1]
            if not city:
                city = loc_dom.xpath('//meta[@name="description"]/@content')[0].replace(
                    "Eye Level ", ""
                )
                if city:
                    street_address = raw_address.split(city)[0].strip()
            city = city if city else "<MISSING>"
            state = structured_adr.state
            state = state if state else "<MISSING>"
            zip_code = structured_adr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = poi["centerNo"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi.get("phone")
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["locLati"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["locLongi"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = poi["centerOpenTime"]
            hours_of_operation = (
                hours_of_operation.replace(",", " ").strip()
                if hours_of_operation
                else "<MISSING>"
            )

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
