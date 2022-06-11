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

    base_link = "https://finleysbarbershop.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "finleysbarbershop.com"

    panels = base.find(class_="vc_tta-panels").find_all(class_="vc_tta-panel")

    for panel in panels:
        loc = panel.find(class_="vc_tta-title-text").text.upper()
        if "AUSTIN" in loc:
            code = "base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"
        elif "DALLAS" in loc:
            code = "base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMopR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABXgWuw"
        elif "DENVER" in loc:
            code = "base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMo5R0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABaMWvA"
        elif "HOUSTON" in loc:
            code = "base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMolR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABc4WvQ"
        else:
            raise

        link = "https://finleysbarbershop.com/wp-json/wpgmza/v1/features/" + code
        stores = session.get(link, headers=headers).json()["markers"]

        for store in stores:
            location_name = store["title"].strip()

            raw_address = (
                store["address"]
                .replace("F620 Westlake", "F620, Westlake")
                .replace("Avenue, Suite", "Avenue Suite")
                .replace("Road, Suite", "Road Suite")
                .replace("4 Green", "4, Green")
                .split(",")
            )

            if len(raw_address) == 3:
                street_address = raw_address[0].strip()
                city = raw_address[1].strip()
            else:
                street_address = " ".join(raw_address[0].split()[:-1]).strip()
                city = raw_address[0].split()[-1].strip()

            state = raw_address[-1].strip()[:-6].upper().strip()
            zip_code = raw_address[-1][-6:].strip()

            country_code = "US"
            store_number = store["id"]
            location_type = "<MISSING>"
            raw_data = BeautifulSoup(store["description"], "lxml")
            phone = raw_data.h4.text.strip()
            hours_of_operation = (
                raw_data.find(class_="loc-txt-descr")
                .p.text.replace("PM", "PM ")
                .replace("OPEN", "")
                .replace("\xa0", " ")
                .strip()
            )
            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

            latitude = store["lat"].strip()
            longitude = store["lng"].strip()

            data.append(
                [
                    locator_domain,
                    "https://finleysbarbershop.com/locations/",
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
