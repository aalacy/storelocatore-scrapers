import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgselenium import SgChrome

logger = SgLogSetup().get_logger("whitscustard_com")


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

    base_link = "https://whitscustard.com/findyourwhits"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    items = base.find(class_="sqs-gallery").find_all("a")
    for i in items:
        main_link = "https://whitscustard.com" + i["href"]
        if "opening-soon" not in main_link:
            main_links.append(main_link)

    final_links = []
    for main_link in main_links:
        if "ohio" not in main_link:
            req = session.get(main_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
        else:
            driver = SgChrome().chrome()
            driver.get(main_link)
            base = BeautifulSoup(driver.page_source, "lxml")
            driver.close()
        items = base.find_all(class_="summary-title-link")
        for i in items:
            if "Opening%2Bsoon" not in str(i):
                final_links.append("https://whitscustard.com" + i["href"])

    data = []
    locator_domain = "whitscustard.com"

    for link in final_links:
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if "Opening%2Bsoon" in str(base):
            continue
        location_name = (
            base.find(class_="entry-title")
            .text.encode("ascii", "replace")
            .decode()
            .replace("?", "-")
            .replace("  ", "")
            .strip()
        )

        raw_address = (
            str(base.address)
            .replace("<address>", "")
            .replace("</address>", "")
            .replace("SUITE 101,", "SUITE 101<br/>")
            .replace("HWY HENDER", "HWY<br/>HENDER")
            .replace("\nSUITE", " SUITE")
            .replace("RD.\n", "RD. ")
            .replace("WEST, \n", "WEST, ")
            .split("<br/>")
        )

        street_address = raw_address[0].strip()
        if street_address == "None" or not street_address:
            try:
                raw_address = list(base.find(id="address").stripped_strings)
            except:
                try:
                    raw_address = list(base.find(class_="pslAddress").stripped_strings)
                    if "\n" in raw_address[0]:
                        raw_address = (
                            raw_address[0].replace("\n", "<br/>").split("<br/>")
                        )
                except:
                    raw_address = base.h3.text.replace("NUE ZAN", "NUE<br/>ZAN").split(
                        "<br/>"
                    )
            street_address = " ".join(raw_address[:-1]).strip()
        if "\n" in street_address:
            raw_address = base.address.text.strip().split("\n")
            street_address = " ".join(raw_address[:-1]).strip()
        city_line = raw_address[-1].strip().split(",")
        if len(city_line) == 2:
            city = city_line[0]
            state = city_line[1].split()[0]
            zip_code = city_line[1].split()[1]
        elif len(city_line) == 3:
            city = city_line[0]
            state = city_line[1].strip()
            zip_code = city_line[2].strip()
        elif len(city_line) == 1:
            city_line = city_line[0].split()
            city = city_line[0]
            state = city_line[1]
            zip_code = city_line[2]
        elif "ORANGE PARK" in location_name:
            street_address = "10 Blanding Blvd, Ste A"
            city = "Orange Park"
            state = "FL"
            zip_code = "32073"
        else:
            raise

        if street_address[-1:] == ",":
            street_address = street_address[:-1]

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone = (
                base.find("a", {"href": re.compile(r"tel")})["href"]
                .replace("tel:", "")
                .strip()
            )
        except:
            phone = "<MISSING>"
        if not phone:
            phone = "<MISSING>"

        hours_of_operation = (
            base.find_all(class_="col sqs-col-3 span-3")[-1]
            .text.replace("Hours", "")
            .replace("PM", "PM ")
            .replace("Drive-thru only", "")
            .replace("losed", "losed ")
            .replace("LOSED", "LOSED ")
            .replace("HOURS", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.encode("ascii", "replace").decode().replace("?", "-")
        )
        if "holiday hours" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("holiday hours")[1].strip()
        hours_of_operation = hours_of_operation.split("(")[0].split("Due to")[0].strip()
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        map_link = ""
        maps = base.find_all("a")
        for i in maps:
            if "Directions" in i.text:
                map_link = i["href"].strip()
                break
        if map_link:
            req = session.get(map_link, headers=headers)
            maps = BeautifulSoup(req.text, "lxml")
            try:
                raw_gps = maps.find("meta", attrs={"itemprop": "image"})["content"]
                latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find("%")].strip()
                longitude = raw_gps[raw_gps.find("-") : raw_gps.find("&")].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if len(latitude) > 20:
            old_lat = latitude
            latitude = old_lat.split("=")[-1].split(",")[0]
            longitude = old_lat.split("=")[-1].split(",")[1]
        if "11362 SAN JOSE BLVD" in street_address.upper():
            latitude = "30.1677275"
            longitude = "-81.6349426"
        if not longitude:
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
