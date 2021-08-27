import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("bbqgalore_com")


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

    base_link = "https://www.bbqgalore.com/stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    main_links = []
    main_items = base.find_all("span", attrs={"style": "font-size: medium;"})
    for main_item in main_items:
        main_link = main_item.a["href"]
        if "http" not in main_link:
            main_link = "https://www.bbqgalore.com" + main_link
        main_links.append(main_link)

    data = []
    for final_link in main_links:
        logger.info(final_link)
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "bbqgalore.com"

        location_name = "Barbeques Galore " + item.find("h2").text.strip().title()
        try:
            raw_address = str(item.find(class_="main-container").find_all("p")[0])[
                3:
            ].split("<br/>")[:2]
            if "location" in raw_address[0].lower():
                raw_address = str(item.find(class_="main-container").find_all("p")[0])[
                    3:
                ].split("<br/>")[2:4]
            if "located in" in raw_address[0].lower():
                raw_address = str(item.find(class_="main-container").find_all("p")[1])[
                    3:
                ].split("<br/>")[:3]
            dealer = False
            location_type = "LOCATION"
        except:
            raw_address = str(item.find(id="left")).split("<br/>")[3:5]
            location_type = "AUTHORIZED DEALER"
            dealer = True

        street_address = raw_address[0].strip()
        city = raw_address[1][: raw_address[1].find(",")].strip()
        state = raw_address[1][raw_address[1].find(",") + 1 : -6].strip()
        zip_code = raw_address[1][-6:].strip()
        country_code = "US"
        store_number = "<MISSING>"

        if not dealer:
            phone = item.find(class_="main-container").a.text.strip()
            hours_of_operation = (
                item.find(class_="main-container")
                .find_all("p")[-1]
                .get_text(" ")
                .strip()
            )
            script = (
                item.find(class_="column main")
                .find("script", attrs={"type": "application/ld+json"})
                .contents[0]
            )
            script = script[script.find("{") : script.rfind("}") + 1].strip()
            geo = json.loads(script)

            latitude = geo["geo"]["latitude"]
            longitude = geo["geo"]["longitude"]
        else:
            phone = item.find(id="left").a.text.strip()
            hours_of_operation = (
                item.find(id="left").find_all("p")[1].text.replace("\n", " ").strip()
            )

            if street_address == "1087 Meridian Ave. Ste 10":
                latitude = "37.304393"
                longitude = "-121.914196"
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

        data.append(
            [
                locator_domain,
                final_link,
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
