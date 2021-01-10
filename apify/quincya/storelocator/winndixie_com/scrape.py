import csv
import json

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

    base_link = "https://www.winndixie.com/locator"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "var locations" in str(script):
            script = (
                script.text.split("=")[1].split("]];")[0].replace("\r\n", "").strip()
                + "]]"
            )
            break

    items = json.loads(script)
    locator_domain = "winndixie.com"

    for item in items:
        store_number = item[0]
        latitude = item[1]
        longitude = item[2]

        type_num = item[3]
        if type_num == "1" or type_num == "2":
            location_type = "Store"
        elif type_num == "3":
            location_type = "Liquor"
        else:
            continue

        link = "https://www.winndixie.com/storedetails?search=" + store_number
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.replace("\xa0", " ").strip()

        raw_address = list(base.find(class_="w-50 Mw-100").a.stripped_strings)
        street_address = (
            raw_address[0].replace(", Lakewood Ranch, Fl 34202", "").strip()
        )
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city = raw_address[-1].split(",")[0].strip()
        state = raw_address[-1].split(",")[1][:-6].strip()
        zip_code = raw_address[-1][-6:].strip()
        country_code = "US"
        phone = base.find(class_="mob_num").text.strip()
        hours_of_operation = (
            " ".join(
                list(
                    base.find(class_="dis-inflex stores_head Mdis-blk w-100")
                    .find(class_="w-50 Mw-100")
                    .stripped_strings
                )
            )
            .replace("Store hours", "")
            .strip()
        )

        if (
            location_type == "Liquor"
            and "Liquor store" in base.find(class_="dis-inflex Mdis-blk w-100").text
        ):
            hours_of_operation = " ".join(
                list(base.find(class_="dis-inflex Mdis-blk w-100").ul.stripped_strings)
            ).strip()

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
