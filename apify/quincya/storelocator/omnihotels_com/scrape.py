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

    base_link = "https://www.omnihotels.com/destinations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "location.href.toLowerCase().indexOf" in str(script):
            script = str(script)
            break

    items = re.findall(r'/hotels/.+"\)', script)
    types = re.findall(r"propstatus = .+;", script)[1:]

    locator_domain = "omnihotels.com"

    for i, item in enumerate(items):
        location_type = types[i].split('"')[1].split('"')[0]
        if "permanently" in location_type or "coming" in location_type:
            continue
        link = "https://www.omnihotels.com" + item[:-2]
        if "cancun" in link:
            continue
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = (
            base.h1.text.replace("welcome to", "")
            .replace("the newly expanded and enhanced", "")
            .replace("coming soon", "")
            .strip()
        )

        raw_address = base.find(class_="plp-hotel-content-container").p.text.split(",")
        street_address = raw_address[0].split("(")[0].strip()
        city = raw_address[1].strip()
        state = " ".join(
            raw_address[2].strip().replace("\xa0", " ").split()[:-1]
        ).strip()
        zip_code = raw_address[2].strip().replace("\xa0", " ").split()[-1].strip()
        if len(zip_code) < 5:
            zip_code = " ".join(raw_address[2].split()[1:]).strip()
            state = raw_address[2].split()[0].strip()
        country_code = "US"
        if len(zip_code) > 5:
            country_code = "CA"

        store_number = "<MISSING>"
        phone = base.find(class_="plp-contact-link plp-phone").text.strip()
        hours_of_operation = "<MISSING>"

        try:
            map_link = base.find(class_="plp-hotel-content-container").p.a["href"]
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_link)[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1]
        except:
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
