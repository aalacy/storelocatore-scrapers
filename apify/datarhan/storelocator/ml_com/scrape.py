import csv
import json
from lxml import etree
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "ml.com"

    start_url = "https://fa.ml.com/find-an-advisor/locator/api/InternalSearch"
    hdr = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    usr_agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    body = '{"Locator":"MER-WM-Offices","PostalCode":"%s","Company":null,"ProfileTypes":"Branch","DoFuzzyNameSearch":0,"SearchRadius":"50"}'

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=None,
    )

    for code in all_codes:
        response = session.post(start_url, data=body % code, headers=hdr)
        if not response.text:
            continue
        data = json.loads(response.text)
        if not data.get("Results"):
            continue
        for poi in data["Results"]:
            store_url = "https:" + poi["XmlData"]["parameters"]["Url"]
            location_name = poi["Company"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["Address1"]
            if poi["Address2"]:
                street_address += ", " + poi["Address2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["City"]
            city = city if city else "<MISSING>"
            state = poi["Region"]
            state = state if state else "<MISSING>"
            zip_code = poi["PostalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["Country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["ProfileId"]
            phone = poi["XmlData"]["parameters"]["LocalNumber"]
            phone = phone if phone else "<MISSING>"
            latitude = poi["GeoLat"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["GeoLon"]
            longitude = longitude if longitude else "<MISSING>"
            location_type = poi["ProfileType"]
            location_type = location_type if location_type else "<MISSING>"

            check = "{} {}".format(location_name, street_address)
            if check in scraped_items:
                continue
            store_response = session.get(store_url, headers=usr_agent)
            store_dom = etree.HTML(store_response.text)
            if store_dom:
                hours_of_operation = store_dom.xpath(
                    '//div[@id="more-hours"]//ul/li/text()'
                )
                hours_of_operation = (
                    " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
                )
            else:
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
            check = "{} {}".format(location_name, street_address)
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
