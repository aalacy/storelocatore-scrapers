import csv
import json
import re

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

    base_link = "https://www.rehab-associates.com//sxa/search/results/?s={8AE60BE8-DF53-49BC-AEAF-CD566CBCEC80}|{A07F1984-B5BC-4E80-90F4-B48D191F4029}&itemid={394D5897-5693-4DF5-AA4C-958F29795C16}&sig=&autoFireSearch=true&v=%7B919C3870-FD24-4AE3-BC68-E9EBB85E2C4E%7D&p=3000&g=&o="

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    new_base = (
        str(base)
        .replace("</li><li>", ",")
        .replace("<br/>", ",,")
        .replace('<img src="h', " ,,DDD")
        .replace('"/>', "DDD,,")
        .replace("Request an Appointment", ",,")
        .replace("Featured Services", ",,")
    )
    final_base = BeautifulSoup(new_base, "lxml")
    store = json.loads(final_base.text)["Results"]

    data = []
    for item in store:
        locator_domain = "rehab-associates.com"

        raw_data = item["Html"].split(",,")
        location_name = raw_data[0].strip()

        location_type = raw_data[-3].replace("DDDt", "ht").replace("DDD", "")
        if "RehabAssociates" not in location_type:
            continue

        if len(raw_data) == 7:
            street_address = raw_data[1].strip() + " " + raw_data[2].strip()
            city_line = raw_data[3].strip()
        else:
            street_address = raw_data[1].strip()
            city_line = raw_data[2].strip()

        city = city_line[: city_line.find(",")].strip()
        state = city_line[city_line.find(",") + 1 : city_line.find(",") + 5].strip()
        zip_code = city_line.split("\r")[0].split()[-1]
        country_code = "US"

        store_number = "<MISSING>"
        phone = city_line.split("\r")[1].strip()

        hours = (
            raw_data[-2]
            .replace("Hours", "")
            .replace("PM", "PM ")
            .replace("Closed", "Closed ")
            .strip()
        )
        hours_of_operation = re.sub(" +", " ", hours)

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        latitude = item["Geospatial"]["Latitude"]
        longitude = item["Geospatial"]["Longitude"]

        location_type = raw_data[-1].strip()

        link = (
            "https://www.rehab-associates.com/contact/find-a-location"
            + item["Url"].split("outpatient")[-1]
        )

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
