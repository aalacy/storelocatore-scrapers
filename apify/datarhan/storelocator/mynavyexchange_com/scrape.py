import re
import csv
import usaddress
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

    DOMAIN = "mynavyexchange.com"
    start_url = "https://www.mynavyexchange.com/storelocator/storeresults.jsp?searchMap=true&state={}"

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    all_locations = []
    for state in states:
        response = session.get(start_url.format(state))
        all_locations += re.findall("storeid=(.+?)&", response.text)

    for store_number in all_locations:
        if not store_number.isdigit():
            continue
        store_url = "https://www.mynavyexchange.com/storelocator/storedetails.jsp?storeid={}&zipcode=&state=CA&radius=&city=&country="
        store_url = store_url.format(store_number)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="storeNameWrapper"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@class="address"]/text()')[0].split("\n")
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = " ".join(raw_address[:2])
        raw_adr_new = " ".join(sorted(set(raw_address), key=raw_address.index))
        street_address = raw_adr_new.split(", ")[0]
        city = [
            elem[0] for elem in usaddress.parse(raw_adr_new) if elem[1] == "PlaceName"
        ]
        city = " ".join(city) if city else "<MISSING>"
        if city == "<MISSING>":
            city = raw_address[2]
        city = city.split("Street")[-1].strip().replace("Building ", "")
        street_address_spilt = street_address.split()
        street_address = " ".join(
            sorted(set(street_address_spilt), key=street_address_spilt.index)
        )
        if street_address.strip().endswith(city):
            street_address = street_address.split(city)[0]
        state = raw_address[-2].replace(",", "")
        zip_code = raw_address[-1]
        country_code = "<MISSING>"
        phone = loc_dom.xpath(
            '//div[contains(text(), "Main:")]/following-sibling::div[@class="phone"][1]/text()'
        )
        phone = (
            phone[0].replace("Customer Service", "").strip() if phone else "<MISSING>"
        )
        location_type = "<MISSING>"
        geo = loc_dom.xpath('//input[@id="endPoint"]/@value')[0].split(",")
        latitude = geo[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[1]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<INACCESIBLE>"

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
