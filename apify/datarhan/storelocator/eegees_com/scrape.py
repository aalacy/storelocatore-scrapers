import csv
import json
import usaddress
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "eegees.com"
    start_url = "https://eegees.com/wp-admin/admin-ajax.php?action=get_locations"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = "<MISSING>"
        location_name = poi["title"]
        location_name = (
            location_name.replace("&#8211;", "").replace("&#8217;", "'")
            if location_name
            else "<MISSING>"
        )
        if poi["address"]:
            address_dict = usaddress.tag(poi["address"])[0]
        else:
            address_dict = usaddress.tag(poi["title"])[0]
        AddressNumber = address_dict.get("AddressNumber")
        AddressNumber = AddressNumber if AddressNumber else " "
        StreetNamePreDirectional = address_dict.get("StreetNamePreDirectional")
        StreetNamePreDirectional = (
            StreetNamePreDirectional if StreetNamePreDirectional else " "
        )
        StreetName = address_dict.get("StreetName")
        StreetName = StreetName if StreetName else " "
        StreetNamePostType = address_dict.get("StreetNamePostType")
        StreetNamePostType = StreetNamePostType if StreetNamePostType else " "
        OccupancyType = address_dict.get("OccupancyType")
        OccupancyType = OccupancyType if OccupancyType else " "
        OccupancyIdentifier = address_dict.get("OccupancyIdentifier")
        OccupancyIdentifier = OccupancyIdentifier if OccupancyIdentifier else " "

        street_address = f"{AddressNumber} {StreetNamePreDirectional} {StreetName} {StreetNamePostType} {OccupancyType} {OccupancyIdentifier}".replace(
            "  ", " "
        )
        city = address_dict.get("PlaceName")
        city = city if city else "<MISSING>"
        state = address_dict.get("StateName")
        state = state if state else "<MISSING>"
        zip_code = address_dict.get("ZipCode")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["category_name"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = etree.HTML(poi["info_popup"])
        hoo = hoo.xpath('//h3[contains(text(), "Store Hours")]/following::text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()][:2]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
