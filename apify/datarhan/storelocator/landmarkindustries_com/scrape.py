import re
import csv
import usaddress
from lxml import etree
from collections import OrderedDict

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

    DOMAIN = "landmarkindustries.com"
    start_url = "https://www.landmarkindustries.com/retail.htm"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_poi = []
    all_locations = dom.xpath('//td[@width="263"]/p/text()')
    all_locations_raw = "".join(all_locations).split("\r\n")

    for elem in all_locations_raw:
        all_poi += elem.strip().split("\n")

    for loc in all_poi:
        if not loc:
            continue
        location_type = "<MISSING>"
        if " Opening Soon!" in loc:
            loc = loc.replace(" Opening Soon!", "")
            location_type = "opening soon"
        loc = loc.replace("\n", "").strip()
        store_url = "<MISSING>"
        location_name = re.findall("(.+ Exxon)", loc)
        if not location_name:
            location_name = re.findall("(.+ Shell)", loc.strip())
        if not location_name:
            location_name = re.findall("(.+ Mobil)", loc.strip())
        location_name = location_name[0] if location_name else "<MISSING>"
        if location_name == "<MISSING>":
            continue
        address_raw = loc.split(location_name)[-1]
        street_address = address_raw.split(",")[0].strip()
        try:
            address_raw = usaddress.tag(address_raw)
            address_raw = OrderedDict(address_raw[0])
            address_raw = dict(address_raw)
        except:
            address_raw = usaddress.parse(address_raw)
            address_raw = OrderedDict(address_raw)
            address_raw = {y: x for x, y in address_raw.items()}
        city = address_raw.get("PlaceName")
        if city:
            street_address = street_address.replace(city, "").strip()
        city = city.replace(",", "") if city else "<MISSING>"
        state = address_raw.get("StateName")
        state = state if state else "<MISSING>"
        zip_code = address_raw.get("ZipCode")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = re.findall(r"\d\d\d", location_name)
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = address_raw.get("OccupancyIdentifier")
        phone = phone if phone else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        # exceptions
        if len(zip_code) == 17:
            phone = zip_code[5:]
            zip_code = zip_code[:5]

        if "Opening Soon" in state:
            raw_data = state
            state = raw_data.split()[0]
            zip_code = raw_data.split()[-1].split("Opening")[0]

        if len(zip_code) == 12:
            phone = zip_code
            zip_code = "<MISSING>"

        check = ["Rd", "Freeway", "Fwy", "Dr", "Road"]
        for elem in check:
            if city.startswith(elem):
                street_address += " " + elem
                city = city.replace(elem, "")
                break

        if city.startswith("SR"):
            city = city.replace("SR", "R")
            street_address += " S"

        if "soon" in zip_code.lower():
            zip_code = "<MISSING>"
            location_type = "opening soon"

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
