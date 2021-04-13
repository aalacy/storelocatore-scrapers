import csv

from bs4 import BeautifulSoup

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

    base_link = "https://pinnacletreatment.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "pinnacletreatment.com"

    sections = base.find(class_="locations-select").find_all("option")[1:]
    for section in sections:
        state_link = section["value"]
        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find(id="locations-grid").find_all("li")

        for item in items:

            location_name = item.h2.text.strip()

            raw_address = list(
                item.find(class_="locations-grid-address").stripped_strings
            )
            street_address = raw_address[-4]
            city = raw_address[-3].split(",")[0].replace("5th St", "").strip()
            state = raw_address[-3].split(",")[1].split()[0]
            zip_code = raw_address[-3].split(",")[1].split()[1]
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            phone = item.find(class_="listing-grid-phone").text.split(",")[0].strip()

            link = item.a["href"]
            req = session.get(link, headers=headers)
            page_base = BeautifulSoup(req.text, "lxml")
            if "coming soon" in page_base.find(class_="entry-content").text.lower():
                continue

            try:
                map_link = page_base.find(id="locations-map").iframe["data-lazy-src"]
                lat_pos = map_link.rfind("!3d")
                latitude = map_link[
                    lat_pos + 3 : map_link.find("!", lat_pos + 5)
                ].strip()
                lng_pos = map_link.find("!2d")
                longitude = map_link[
                    lng_pos + 3 : map_link.find("!", lng_pos + 5)
                ].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            try:
                hours_of_operation = " ".join(
                    page_base.find(class_="right")
                    .text.strip()
                    .split("\n\r\n")[0]
                    .split("Hours:")[1:]
                ).strip()
                if len(hours_of_operation) < 10:
                    hours_of_operation = (
                        page_base.find(class_="right")
                        .text.strip()
                        .split("\n\r\n")[0]
                        .split("Hours:")[2]
                        .strip()
                    )

                hours_of_operation = (
                    hours_of_operation.replace("\r\n", " ")
                    .replace("\nGroups:", " Groups:")
                    .split("\n")[0]
                    .replace("Clinic:", "")
                    .replace("Clinic", "")
                    .replace("We're open", "")
                    .strip()
                )

                if hours_of_operation == "Dispensing:":
                    hours_of_operation = (
                        " ".join(
                            page_base.find(class_="right")
                            .text.strip()
                            .split("\n\r\n")[0]
                            .split("Office Hours:")[1:]
                        )
                        .strip()
                        .split("\n")[0]
                        .strip()
                    )

                if hours_of_operation == "Hours of Operation:":
                    hours_of_operation = (
                        " ".join(
                            page_base.find(class_="right")
                            .text.strip()
                            .split("Operation:\n\r\n")[1:]
                        )
                        .split("\n\r\n")[0]
                        .replace("\r\n", " ")
                    ).strip()
            except:
                hours_of_operation = "<MISSING>"

            if " Hours" in hours_of_operation:
                hours_of_operation.split(" Hours")[1].strip()

            hours_of_operation = (
                hours_of_operation.split("*")[0]
                .replace("Administrative", "")
                .replace("Office", "")
                .replace("Office:", "")
                .replace("Dispensing", "")
                .replace("Medication", "")
                .replace("Methadone:", "")
                .replace("Dosing", "")
                .replace(": Mon", "Mon")
                .replace("  ", " ")
            ).strip()

            if "Hours " in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Hours ")[1].strip()

            data.append(
                [
                    locator_domain,
                    link,
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
            )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
