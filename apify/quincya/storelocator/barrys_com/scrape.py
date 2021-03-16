import csv
import re

from bs4 import BeautifulSoup

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

    base_link = "https://www.barrys.com/studios/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    all_links = []

    locator_domain = "barrys.com"

    countries = ["usa", "canada", "united-kingdom"]
    for country in countries:
        if country == "usa":
            country_code = "US"
        elif country == "canada":
            country_code = "CA"
        else:
            country_code = "UK"
        items = (
            base.find(id=country)
            .find_next_sibling("div")
            .find_all(class_="grid__item card-studio")
        )
        for i in items:
            link = "https://www.barrys.com" + i["href"]
            if "at-home" in link or "comingsoon" in str(i):
                continue
            all_links.append([country_code, link])

    for i in all_links:
        country_code = i[0]
        link = i[1]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = list(
            base.find(
                class_="grid__item wysiwyg two-up__item two-up__item--content"
            ).stripped_strings
        )[1:]

        if "COMING SOON" in str(raw_address).upper():
            continue

        if "Rooftop" in raw_address[0]:
            raw_address.pop(0)

        location_name = base.h1.text.strip()
        street_address = raw_address[0].split("(")[0].replace("New York", "").strip()
        city_line = (
            raw_address[1].replace("CA, ", "CA ").replace("NY, ", "NY ").split(",")
        )

        if country_code == "US":
            if "hours" in city_line[0]:
                city_line = " ".join(street_address.split(",")[1:]).split(",")
                street_address = street_address.split(",")[0].strip()
            if "2140 South Boulevard" in street_address:
                city_line = "Charlotte, NC 28203".split(",")
            if len(city_line) == 3:
                street_address = city_line[0].strip()
                city_line.pop(0)
            if "112 E 11th" in street_address:
                street_address = street_address.split(",")[0].strip()
                city_line = "New York, NY 10003".split(",")
            if "72-74 W" in street_address:
                street_address = "72-74 W. 69th St New York"
                city_line = "New York, NY 10023".split(",")
            city = city_line[0].strip()
            state = city_line[1].split()[0].strip()
            zip_code = city_line[1].split()[1].strip()
            if "2 Marina Blvd" in street_address:
                state = "New York"
                zip_code = "10023"
        elif country_code == "CA":
            if "2306 4th Street" in street_address:
                street_address = "2306 4th Street SW"
                city_line = "Calgary, AB T2S1X2".split(",")
            if "100 Bloor St. W" in street_address:
                street_address = "100 Bloor St. W"
                city_line = "Toronto, Ontario M5S3L7".split(",")
            city = city_line[0].strip()
            state = city_line[1].split()[0].strip()
            zip_code = city_line[1].split()[1].strip()
        else:
            city = city_line[0].strip()
            state = "<MISSING>"
            zip_code = " ".join(raw_address[1].split()[-2:]).strip()
            if "london" in location_name.lower():
                city = "London"
            if "16 Eccleston Yards" in street_address:
                street_address = street_address + " Eccleston Place"
            if "Kingly Street" in street_address:
                street_address = "59 Kingly Street, Soho"
                zip_code = "W1B 5QL"
        if street_address[-1:] == ",":
            street_address = street_address[:-1].strip()
        state = state.replace(".", "")

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        raw_text = base.find(
            class_="grid__item wysiwyg two-up__item two-up__item--content"
        ).text
        try:
            phone = re.findall(r"[\d]{1}.+[\d]{3}.+[\d]{4}", raw_text)[0]
        except:
            phone = "<MISSING>"

        found_hours = False
        hours_of_operation = ""
        for p in raw_address:
            if not found_hours:
                if "hours" in p.lower():
                    found_hours = True
                continue
            else:
                if "contact" not in p.lower():
                    hours_of_operation = (hours_of_operation + " " + p).strip()
                else:
                    break

        if "Operation" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Operation")[1].strip()

        hours_of_operation = (
            hours_of_operation.split("Parking")[0].replace("\xa0", " ").strip()
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        if "coming" in hours_of_operation.lower():
            continue

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
