import csv
from lxml import etree

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "https://www.dentalservice.net"
    scraped_items = []

    r = session.get(
        "https://www.dentalservice.net/contact-us/find-your-office/", headers=headers
    )
    dom = etree.HTML(r.text)
    data_id = dom.xpath("//script/@data-id")[0]

    r = session.get(
        "https://locator-api.localsearchprofiles.com/api/LocationSearchResults/?configuration="
        + data_id
        + "&start=0",
        headers=headers,
        verify=False,
    )
    json_data = r.json()
    all_locations = json_data["Hit"]
    for i in range(10, json_data["Found"] + 10, 10):
        r = session.get(
            "https://locator-api.localsearchprofiles.com/api/LocationSearchResults/?configuration="
            + data_id
            + "&start="
            + str(i),
            headers=headers,
            verify=False,
        )
        json_data = r.json()
        all_locations += json_data["Hit"]

    for location in all_locations:
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        hours_of_operation = ""
        page_url = ""

        store_number = location["Id"].replace("-", "")
        street_address = location["Fields"]["Address1"][0]
        location_name = location["Fields"]["LocationName"][0]
        if "Address2" in location["Fields"]:
            street_address += " " + location["Fields"]["Address2"][0]

        city = location["Fields"]["City"][0]
        state = location["Fields"]["State"][0]
        zipp = location["Fields"]["Zip"][0]
        phone = location["Fields"]["Phone"][0]
        page_url = location["Fields"]["Url"][0]
        latitude = location["Fields"]["Latlng"][0].split(",")[0]
        longitude = location["Fields"]["Latlng"][0].split(",")[1]

        hours_of_operation = ""
        if "HoursOfOperation" in location:
            hours_day = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            for day in hours_day:
                hours_of_operation += (
                    str(day)
                    + " "
                    + str(location["HoursOfOperation"][str(day)]["Hours"][0])
                    .replace("{", "")
                    .replace("}", "")
                    .replace("'", "")
                    + " "
                )
        hours_of_operation = (
            hours_of_operation.replace(", CloseTime: ", " - ")
            .replace("CloseTime: ", "")
            .replace("OpenTime: ", "")
        )
        store = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
            page_url,
        ]

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
