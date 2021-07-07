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

    base_link = "https://www.weberlogistics.com/locations/west-coast-warehousing"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    links = base.find(class_="span6").find_all("a")

    data = []

    items = base.find_all(class_="interactive-map-tabs-item")
    locator_domain = "weberlogistics.com"

    for i, item in enumerate(items):

        raw_address = list(item.stripped_strings)[1:]
        street_address = raw_address[0].strip()
        city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "Distribution Center"
        try:
            phone = raw_address[2]
        except:
            phone = "<MISSING>"
        hours_of_operation = "<MISSING>"

        link = "https://www.weberlogistics.com" + item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()

        try:
            map_link = base.iframe["src"]
            req = session.get(map_link, headers=headers)
            map_str = BeautifulSoup(req.text, "lxml")
            geo = (
                re.findall(r"\[[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]", str(map_str))[0]
                .replace("[", "")
                .replace("]", "")
                .split(",")
            )
            latitude = geo[0]
            longitude = geo[1]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        for i in links:
            try:
                if i["data-link"] == link:
                    if i["class"][-1] == "style-03-blue":
                        location_type = "Transportation Service Center"
                    if i["class"][-1] == "style-02":
                        location_type = (
                            "Distribution Center & Transportation Service Center"
                        )
                    break
            except:
                pass

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
