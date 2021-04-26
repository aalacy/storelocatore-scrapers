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

    base_link = "https://gussbbq.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="ContainerGroup clearfix")[1].find_all("a")
    locator_domain = "gussbbq.com"

    for item in items:
        link = "https://gussbbq.com/" + item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = item.text

        raws = base.find_all(class_="clearfix grpelem shared_content")
        for raw in raws:
            if "contact us" in raw.text.lower():
                raw_data = raw
                break

        raw_hours = base.find_all(
            class_="rounded-corners clearfix grpelem shared_content"
        )
        for raw in raw_hours:
            if "hours" in raw.text.lower():
                raw_hour = raw
                break

        raw_address = list(raw_data.stripped_strings)
        street_address = " ".join(raw_address[1:-3]).strip()
        city_line = raw_address[-3].split(",")
        if not city_line[1]:
            city = raw_address[-4].replace(",", "")
            state = raw_address[-3].split()[0]
            zip_code = raw_address[-3].split()[1]
        else:
            city = city_line[0].strip()
            state = city_line[1].strip()[:-6].strip()
            zip_code = city_line[1][-6:].strip()
        phone = re.findall(
            r"[0-9]{3}-[0-9]{3}-[0-9]{4}",
            raw_data.text,
        )[0]
        hours_of_operation = (
            " ".join(list(raw_hour.stripped_strings)).replace("HOURS", "").strip()
        )

        country_code = "US"
        store_number = "<MISSING>"

        location_type = "<MISSING>"

        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "LatLng" in str(script):
                map_link = str(script)
                break

        try:
            at_pos = map_link.find("LatLng")
            latitude = map_link[at_pos + 7 : map_link.find(",", at_pos)].strip()
            longitude = map_link[
                map_link.find(",", at_pos) + 1 : map_link.find(")", at_pos)
            ].strip()
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
