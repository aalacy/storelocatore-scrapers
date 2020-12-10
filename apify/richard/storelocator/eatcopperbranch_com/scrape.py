from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re


COMPANY_URL = "https://eatcopperbranch.com"

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
    # store data
    store_numbers = []
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    latitude_list = []
    longitude_list = []
    hours = []
    coming_soon = []
    data = []

    base_link = "https://eatcopperbranch.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t=1565644279976"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)

    link = "https://eatcopperbranch.com/locations/"

    lists = BeautifulSoup(req.text,"lxml").find_all("item")

    for item in lists:
        location_title = (
            item.location.renderContents().decode("utf-8")
            if item.location.renderContents()
            else "<MISSING>"
        )
        street_address = (
            item.address.renderContents().decode("utf-8")
            if item.address.renderContents()
            else "<MISSING>"
        )
        street_address = street_address.replace(";#39;","'").replace("Bramalea City Centre","").replace("Yonge Sheppard Centre","")
        latitude = (
            item.latitude.renderContents().decode("utf-8")
            if item.latitude.renderContents()
            else "<MISSING>"
        )
        longitude = (
            item.longitude.renderContents().decode("utf-8")
            if item.longitude.renderContents()
            else "<MISSING>"
        )
        phone_number = (
            item.telephone.renderContents().decode("utf-8")
            if item.telephone.renderContents()
            else "<MISSING>"
        )

        hour = (
            item.operatinghours.renderContents()
            .decode("utf-8")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
        )
        hour = (
            re.sub("<[^>]*>", "", hour)
            if hour != re.sub("<[^>]*>", "", hour)
            else "<MISSING>"
        )
        opening_soon = item.opening_soon

        hour = (hour.replace("PM","PM ").replace("day","day ").replace("losed","losed ")).replace("  "," ")

        # Location title
        locations_titles.append(
            location_title.replace("&amp", "").replace(";#44;", "").replace(";#39;","'")
        ) if location_title.replace("&amp", "").replace(
            ";#44;", ""
        ) != "" else locations_titles.append(
            "<MISSING>"
        )

        # Street Address
        street_addresses.append(
            street_address.replace("&amp", "")
            .replace(";#44;", "")
            .strip()
            .split(",")[0]
            .strip()
            .split("  ")[0]
            .strip()
        ) if street_address.replace("&amp", "").replace(";#44;", "").strip().split(
            "  "
        )[
            -1
        ].strip()[
            :-7
        ] != "" else street_addresses.append(
            "<MISSING>"
        )

        # City
        cities.append(
            street_address.replace("&amp", "")
            .replace(";#44;", "")
            .strip()
            .split(",")[0]
            .strip()
            .split("  ")[1]
            .strip()
        ) if street_address.replace("&amp", "").replace(";#44;", "").strip().split(
            "  "
        )[
            -1
        ].strip()[
            :-7
        ] != "" else cities.append(
            "<MISSING>"
        )

        # Zip code
        zip_find = re.search(
            "([A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1})|(\d{5}$)",
            street_address.replace("&amp", "")
            .replace(";#44;", "")
            .strip()
            .split("  ")[-1]
            .strip(),
        )
        zip_codes.append(zip_find.group(0) if zip_find else "<MISSING>")

        # Province
        state = (
            street_address.replace("&amp", "")
            .replace(";#44;", "")
            .strip()
            .split("  ")[-1]
            .strip()
        )
        if state == "":
            states.append("<MISSING>")
        else:
            if zip_find:
                states.append(state.replace(zip_find.group(0), ""))
            else:
                states.append(state)

        # Latitude
        latitude_list.append(latitude) if latitude != "" else latitude_list.append(
            "<MISSING>"
        )

        # Longitude
        longitude_list.append(longitude) if longitude != "" else longitude_list.append(
            "<MISSING>"
        )

        # Phone
        phone_numbers.append(
            phone_number
        ) if phone_number != "" else phone_numbers.append("<MISSING>")

        # Hour
        hours.append(hour) if hour != "" else hours.append("<MISSING>")
        coming_soon.append(opening_soon)

    # Store data
    for (
        locations_title,
        street_address,
        city,
        state,
        zipcode,
        phone_number,
        latitude,
        longitude,
        hour,
        opening_soon,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
        hours,
        coming_soon,
    ):
        if opening_soon:
            pass
        else:
            data.append(
                [
                    COMPANY_URL,
                    link,
                    locations_title,
                    street_address,
                    city,
                    state,
                    zipcode,
                    "CA",
                    "<MISSING>",
                    phone_number,
                    "<MISSING>",
                    latitude,
                    longitude,
                    hour,
                ]
            )

    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
