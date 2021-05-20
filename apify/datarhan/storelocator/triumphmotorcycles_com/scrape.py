import csv
from urllib.parse import urljoin
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

    DOMAIN = "triumphmotorcycles.com"

    start_url = "https://www.triumphmotorcycles.com/api/v2/places/alldealers?LanguageCode=en-US&SiteLanguageCode=en-US&Skip=0&Take=500&CurrentUrl=www.triumphmotorcycles.com"

    response = session.get(start_url).json()
    all_locations = response["DealerCardData"]["DealerCards"]

    for poi in all_locations:
        store_url = urljoin(start_url, poi["DealerUrl"])
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["Title"]
        location_name = location_name if location_name else "<MISSING>"

        raw_address = f"{poi['AddressLine1']} {poi['AddressLine2']} {poi['AddressLine3']} {poi['AddressLine4']}"
        addr = parse_address_intl(raw_address.replace("<br/>", " "))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        if not zip_code:
            zip_code = poi["PostCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        if poi["OpeningTimes"]:
            hoo = etree.HTML(poi["OpeningTimes"]).xpath("//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = ", ".join(hoo) if hoo else "<MISSING>"

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
