import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

log = SgLogSetup().get_logger("altaconvenience.com")


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

    base_link = "http://altaconvenience.com/Find-a-Store"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="location")

    locator_domain = "altaconvenience.com"

    for item in items:
        if "http" not in item.a["href"]:
            link = "http://altaconvenience.com" + item.a["href"]
        else:
            link = item.a["href"]
        log.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            raw_data = list(base.find(class_="location-info row").p.stripped_strings)
            got_page = True
        except:
            raw_data = list(item.stripped_strings)
            got_page = False

        if got_page:
            location_name = base.h1.text.strip()
            street_address = raw_data[0].strip()
            city_line = raw_data[1].split()
            if city_line[-1].strip().isdigit():
                city = " ".join(city_line[:-2]).replace(",", "").strip()
                state = city_line[-2].replace(".", "").strip()
                zip_code = city_line[-1].strip()
            else:
                city = " ".join(city_line[:-1]).replace(",", "").strip()
                state = city_line[-1].replace(".", "").strip()
                zip_code = "<MISSING>"
            country_code = "US"
            try:
                phone = raw_data[2].replace("Phone:", "").strip()
                if "-" not in phone:
                    phone = list(item.stripped_strings)[-1]
            except:
                phone = "<MISSING>"
            store_number = location_name.split("#")[1].strip()
            location_type = "<MISSING>"

            try:
                hours_of_operation = (
                    " ".join(raw_data[3:])
                    .replace("Hours S", "S")
                    .replace("Hours:", "")
                    .replace("\xa0", " ")
                    .replace("\u200b", " ")
                    .replace("  ", " ")
                    .strip()
                )
            except:
                hours_of_operation = "<MISSING>"

            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
            if "Hours" in hours_of_operation[:5]:
                hours_of_operation = hours_of_operation[5:].strip()

            map_link = base.iframe["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
            if not latitude[-3:].isdigit():
                if "http" not in map_link:
                    map_link = "https:" + map_link
                req = session.get(map_link, headers=headers)
                maps = BeautifulSoup(req.text, "lxml")

                try:
                    raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
                    latitude = raw_gps[
                        raw_gps.find("=") + 1 : raw_gps.find("%")
                    ].strip()
                    longitude = raw_gps[raw_gps.find("-") : raw_gps.find("&")].strip()
                except:
                    latitude = "<INACCESSIBLE>"
                    longitude = "<INACCESSIBLE>"

            if "hours" in phone.lower():
                hours_of_operation = (
                    phone.replace("Hours:", "") + " " + hours_of_operation
                ).strip()
                raw_data = list(item.stripped_strings)
                city_line = raw_data[2].split()
                city = " ".join(city_line[:-2]).replace(",", "").strip()
                state = city_line[1].replace(".", "").strip()
                zip_code = city_line[-1].strip()
                phone = raw_data[-1].strip()
        else:
            location_name = raw_data[0].strip()
            street_address = raw_data[1].strip()
            city_line = raw_data[2].split()
            city = " ".join(city_line[:-2]).replace(",", "").strip()
            state = city_line[1].replace(".", "").strip()
            zip_code = city_line[-1].strip()
            country_code = "US"
            phone = raw_data[-1].strip()
            store_number = location_name.split()[-1].strip()
            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if "conoco-6008" in link.lower():
            store_number = "6008"
            location_name = "Alta Convenience Store #6008"

        yield [
            locator_domain,
            link,
            location_name,
            street_address,
            city,
            state.replace(",", ""),
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
