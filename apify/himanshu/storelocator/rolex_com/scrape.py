import csv
from lxml import etree
from urllib.parse import urljoin

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
    items = []
    session = SgRequests()
    domain = "rolex.com"

    all_locations = session.get(
        "https://retailers.rolex.com/v2/app/establishments/light/jsFront?establishmentType=STORE&langCode=en&brand=RLX&countryCodeGeofencing=US"
    ).json()
    for poi in all_locations:
        store_url = urljoin("https://www.rolex.com/rolex-dealers/", poi["urlRolexSeo"])
        location_name = etree.HTML(poi["nameTranslated"]).xpath("//text()")
        location_name = (
            " ".join([e.strip() for e in location_name])
            .replace("\u202d", "")
            .replace("\u202c", "")
        )
        street_address = poi["streetAddress"].replace("<br/>", " ")
        addr = parse_address_intl(poi["address"].replace("<br/>", " "))
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        if zip_code in ["00000", "n/a"]:
            zip_code = "<MISSING>"
        store_number = poi["rolexId"]
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        phone = poi["phone1"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["type"]
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = []
        for h_data in poi["hoursTranslatedDetails"]:
            day = h_data["dayNameTranslated"]
            if not h_data["isClosed"]:
                hours = h_data["hoursDayTranslated"]
                hoo.append(f"{day} {hours}")
            else:
                hoo.append(f"{day} closed")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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


scrape()
