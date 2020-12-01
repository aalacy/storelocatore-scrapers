import csv
import sgzip
from lxml import etree
from sgzip import SearchableCountries

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

    DOMAIN = "martinizing.com"
    start_url = "https://www.martinizing.com/genxml.php?lat={}&lng={}&radius=100&filter=&services_offered=1,2,3"

    all_coordinates = []
    ca_coords = sgzip.coords_for_radius(
        radius=100, country_code=SearchableCountries.CANADA
    )
    for coord in ca_coords:
        all_coordinates.append(coord)
    us_coords = sgzip.coords_for_radius(
        radius=100, country_code=SearchableCountries.USA
    )
    for coord in us_coords:
        all_coordinates.append(coord)

    for coord in all_coordinates:
        lat, lng = coord
        response = session.get(start_url.format(lat, lng))
        dom = etree.HTML(response.text)

        all_poi = dom.xpath("//marker")
        for poi in all_poi:
            store_url = poi.xpath("@url")
            store_url = store_url[0].strip() if store_url else ""
            store_url = store_url if store_url else "<MISSING>"
            location_name = poi.xpath("@name")
            location_name = location_name[0] if location_name else "<MISSING>"
            street_address = poi.xpath("@address")
            if "MARTINIZING DELIVERS" in street_address[0]:
                continue
            street_address = (
                street_address[0].split("<br>")[0] if street_address else "<MISSING>"
            )
            city = poi.xpath("@address")
            city = city[0].split("<br>")[-1].split()[0] if city else "<MISSING>"
            state = poi.xpath("@address")
            zip_code = poi.xpath("@address")
            len_check = len(state[0].split("<br>")[-1].split())
            if len_check == 3:
                state = state[0].split("<br>")[-1].split()[-2] if state else "<MISSING>"
                zip_code = (
                    zip_code[0].split("<br>")[-1].split()[-1]
                    if zip_code
                    else "<MISSING>"
                )
            if len_check == 4:
                len_last_elem = len(state[0].split("<br>")[-1].split()[-1])
                if len_last_elem == 3:
                    state = (
                        state[0].split("<br>")[-1].split()[-3] if state else "<MISSING>"
                    )
                    zip_code = (
                        " ".join(zip_code[0].split("<br>")[-1].split()[-2:])
                        if zip_code
                        else "<MISSING>"
                    )
                else:
                    state = (
                        state[0].split("<br>")[-1].split()[-2] if state else "<MISSING>"
                    )
                    zip_code = (
                        zip_code[0].split("<br>")[-1].split()[-1]
                        if zip_code
                        else "<MISSING>"
                    )
                    city = " ".join(
                        poi.xpath("@address")[0].split("<br>")[-1].split()[:-2]
                    )
            if len_check == 5:
                state = state[0].split("<br>")[-1].split()[-2] if state else "<MISSING>"
                zip_code = (
                    zip_code[0].split("<br>")[-1].split()[-1]
                    if zip_code
                    else "<MISSING>"
                )
                city = (
                    " ".join(poi.xpath("@address")[0].split("<br>")[-1].split()[:-2])
                    if city
                    else "<MISSING>"
                )
            country_code = ""
            country_code = country_code if country_code else "<MISSING>"
            store_number = ""
            store_number = store_number if store_number else "<MISSING>"
            phone = poi.xpath("@phone")
            phone = phone[0] if phone else "<MISSING>"
            location_type = ""
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi.xpath("@lat")
            latitude = latitude[0] if latitude else "<MISSING>"
            longitude = poi.xpath("@lng")
            longitude = longitude[0] if longitude else "<MISSING>"
            hours_of_operation = []
            days = ["sat", "mon", "tue", "wed", "thu", "fri", "sun"]
            for day in days:
                hours = poi.xpath("@{}".format(day))[0]
                hours_of_operation.append("{} {}".format(day, hours))
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
