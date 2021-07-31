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

    base_link = "https://www.honeydewdonuts.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="col-md-3").find_all("div", recursive=False)

    data = []
    for item in items:
        locator_domain = "honeydewdonuts.com"

        try:
            raw_text = (
                str(item)
                .replace("\r\n", "")
                .replace(":", '":"')
                .replace(",", '",')
                .replace('" "', '"')
                .replace('""', '"')
                .replace("   ", '"')
                .split("storeLocation")[1]
                .strip()
            )
            raw_text = (re.sub('"+', '"', raw_text)).strip()
            script = raw_text[raw_text.find("=") + 1 : raw_text.rfind("}") + 1].replace(
                '"phone":",', '"phone":"",'
            )
            store = json.loads(script)
            got_script = True
        except:
            got_script = False

        location_type = "<MISSING>"
        if got_script:
            location_name = store["name"]
            street_address = store["address"]
            city = store["city"]
            state = store["state"]
            zip_code = store["zipCode"]
            country_code = "US"
            phone = store["phone"]
            if not phone:
                phone = "<MISSING>"
            latitude = store["latitude"].strip()
            longitude = store["longitude"].strip()
        else:
            raw_address = list(item.stripped_strings)
            location_name = raw_address[0]
            street_address = location_name
            city_line = raw_address[1].strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            if "phone" in raw_address[2].lower():
                phone = raw_address[2].replace("Phone:", "").strip()
                if "DRIVE" in phone:
                    location_type = "DRIVE " + phone.split("DRIVE")[1].strip()
                    phone = phone.split("DRIVE")[0].strip()
            else:
                phone = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        store_number = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
