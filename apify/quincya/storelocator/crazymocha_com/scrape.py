import csv
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

    base_link = "https://crazymocha.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    items = base.findAll("p", attrs={"style": "white-space:pre-wrap;"})[1:]

    data = []
    for item in items:
        locator_domain = "crazymocha.com"
        if not item.text.strip():
            continue
        location_name = item.find("strong").text.strip()
        raw_data = (
            str(item)
            .replace("<p>", "")
            .replace("</p>", "")
            .replace("\n", "")
            .replace("\xa0", "")
            .split("<br/>")
        )
        street_address = raw_data[1][
            raw_data[1].rfind(">") + 1 : raw_data[1].find(",")
        ].strip()
        if street_address:
            city = raw_data[1][
                raw_data[1].find(",") + 1 : raw_data[1].rfind(",")
            ].strip()
            state = raw_data[1][
                raw_data[1].rfind(",") + 1 : raw_data[1].rfind(",") + 4
            ].strip()
            zip_code = raw_data[1][
                raw_data[1].rfind(",") + 4 : raw_data[1].rfind(",") + 10
            ].strip()
        else:
            street_address = raw_data[0][
                raw_data[0].rfind(">") + 1 : raw_data[0].find(",")
            ].strip()
            city = raw_data[0][
                raw_data[0].find(",") + 1 : raw_data[0].rfind(",")
            ].strip()
            state = raw_data[0][
                raw_data[0].rfind(",") + 1 : raw_data[0].rfind(",") + 4
            ].strip()
            zip_code = raw_data[0][
                raw_data[0].rfind(",") + 4 : raw_data[0].rfind(",") + 10
            ].strip()
        try:
            int(zip_code)
        except:
            if "Brighton Rehabilitation" in location_name:
                state = "PA"
                city = raw_data[1][
                    raw_data[1].find(",") + 1 : raw_data[1].find(state)
                ].strip()
                zip_code = raw_data[1][raw_data[1].rfind(" ") + 1 :].strip()
        if "Suite" in city:
            street_address = street_address + " " + city[: city.find(",")]
            city = city[city.rfind(" ") :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        try:
            phone = re.findall(r"[(\d)]{5} [\d]{3}-[\d]{4}", item.text)[0]
        except:
            phone = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        hours_of_operation = raw_data[-1].replace("\n", " ").replace("\xa0", "").strip()
        try:
            location_type = re.findall(r"\(.+\)", hours_of_operation)[0][1:-1]
        except:
            location_type = "<MISSING>"

        if "<" in hours_of_operation:
            hours_of_operation = hours_of_operation[
                : hours_of_operation.find("<")
            ].strip()
        hours_of_operation = re.sub(" +", " ", hours_of_operation)

        if not hours_of_operation:
            hours_of_operation = (
                raw_data[-2].replace("\n", " ").replace("\xa0", "").strip()
            )
            hours_of_operation = re.sub(" +", " ", hours_of_operation)

        data.append(
            [
                locator_domain,
                base_link,
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
