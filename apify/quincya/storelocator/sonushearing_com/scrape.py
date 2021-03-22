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

    base_link = "https://www.sonushearing.com/california-counties"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    loc_links = [
        "https://www.sonushearing.com/arlington",
        "https://www.sonushearing.com/fremont-michigan",
        "https://www.sonushearing.com/ludington",
        "https://www.sonushearing.com/golden-valley",
        "https://www.sonushearing.com/whitehall",
        "https://www.sonushearing.com/rockford",
        "https://www.sonushearing.com/allendale",
        "https://www.sonushearing.com/grand-rapids",
        "https://www.sonushearing.com/kalamazoo",
        "https://www.sonushearing.com/muskegon",
        "https://www.sonushearing.com/west-allis",
        "https://www.sonushearing.com/wyoming",
        "https://www.sonushearing.com/long-beach-2",
        "https://www.sonushearing.com/grand-haven",
    ]

    locator_domain = "sonushearing.com"
    items = base.find_all(class_="font_8")
    drop_items = base.find(id="DrpDwnMn14").find_all("a")

    for item in items:
        if item.a:
            loc_links.append(item.a["href"])

    for item in drop_items:
        link = item["href"]
        if "california" not in link and link not in loc_links:
            loc_links.append(link)

    for link in loc_links:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            map_link = base.find("a", string="Directions")["href"]
        except:
            continue

        location_name = (
            base.find_all(class_="font_4")[-1].text.replace("  ", " ").strip()
        )
        if "We are now seeing" in location_name:
            continue

        rows = base.find_all(class_="_1Z_nJ")

        for row in rows:
            if "phone:" in row.text.lower():
                raw_address = (
                    row.text.replace("\u200b", "").split("Phone")[0].strip().split("\n")
                )
                break
        if "phone:" not in row.text.lower():
            raw_address = list(base.find(class_="font_8").stripped_strings)

        street_address = " ".join(raw_address[:-1]).strip()
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "Location"

        if "location is independently owned" in base.text:
            location_type = "Independently Owned"

        try:
            phone = (
                re.findall(
                    r"Phone:.+[\d]{3}-[\d]{4}",
                    str(base),
                )[0]
                .replace("Phone:", "")
                .strip()
            )
        except:
            try:
                phone = re.findall(
                    r"[\d]{3}-[\d]{3}-[\d]{4}",
                    str(base),
                )[0].strip()
            except:
                try:
                    phone_rows = base.find_all(class_="font_3")
                    for phone_row in phone_rows:
                        if "phone:" in phone_row.text.lower():
                            phone = phone_row.text.replace("Phone:", "")
                            break
                except:
                    phone = "<MISSING>"
        phone = phone.replace("&#160;", " ").strip()

        if ">" in phone:
            phone = phone.split(">")[1].strip()

        if "-" not in phone:
            if "850-8800" in str(base):
                phone = "(616) 850-8800"
            else:
                phone = "<MISSING>"

        hours_of_operation = "<MISSING>"
        for row in rows:
            if "hours of operation" in row.text.lower():
                hours_of_operation = (
                    row.text.split("tion")[1]
                    .split("*")[-1]
                    .split("Weekend")[0]
                    .replace("\n", " ")
                    .strip()
                )
                break
        try:
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_link)[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1]
        except:
            req = session.get(map_link, headers=headers)
            maps = BeautifulSoup(req.text, "lxml")

            try:
                raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
                latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find("%")].strip()
                longitude = raw_gps[raw_gps.find("-") : raw_gps.find("&")].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
        if "7230 Medical Center Drive" in street_address:
            latitude = "34.2016729"
            longitude = "-118.6311208"

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
