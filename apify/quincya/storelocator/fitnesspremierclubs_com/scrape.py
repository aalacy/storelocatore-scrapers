import csv
import json
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("fitnesspremierclubs_com")


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

    base_link = "https://www.fitnesspremierclubs.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find(id="top-menu").ul.find_all("a")
    locator_domain = "fitnesspremierclubs.com"

    for item in items:

        link = item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()

        try:
            club_number = re.findall(r"clubNumber=(\d+)", str(base))[0]
        except:
            continue
        logger.info(link)
        club_url = (
            "https://mico.myiclubonline.com/iclub/club/getClubExternal.htm?club=%s&_=1564200271209"
            % club_number
        )
        add_req = session.get(club_url, headers=headers)
        address_base = str(BeautifulSoup(add_req.text, "lxml"))
        add_json = json.loads(
            address_base[address_base.find("{") : address_base.rfind("}") + 1].replace(
                "\n", ""
            )
        )

        street_address = (add_json["address1"] + " " + add_json["address2"]).strip()
        city = add_json["city"]
        state = add_json["state"]
        zip_code = add_json["zip"]
        country_code = "US"
        store_number = add_json["number"]
        location_type = ", ".join(
            list(base.find_all(class_="et_pb_module")[1].stripped_strings)
        ).replace("\xa0", "")
        if len(location_type) < 20:
            location_type = ", ".join(
                list(base.find_all(class_="et_pb_module")[2].stripped_strings)
            ).replace("\xa0", "")
        phone = base.find_all("h4")[1].a["href"].replace("tel:", "")
        hours_of_operation = " ".join(
            list(base.find_all(class_="et_pb_module")[5].stripped_strings)[1:]
        )
        if "day" not in hours_of_operation:
            hours_of_operation = "<MISSING>"

        try:
            map_link = base.find("iframe")["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
            if not latitude[:1].isdigit():
                latitude = "<MISSING>"
                longitude = "<MISSING>"
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
