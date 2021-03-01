import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("thecomfycow_com")


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

    base_link = "https://www.thecomfycow.com/contact-us/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    maps = base.findAll("div", attrs={"class": "map-marker"})
    items = base.find_all("p")[:-1]
    data = []
    found_poi = []

    for i, item in enumerate(items):
        locator_domain = "thecomfycow.com"
        try:
            location_name = item.find("span").text.strip()
        except:
            continue
        if location_name in found_poi:
            continue

        found_poi.append(location_name)
        logger.info(location_name)

        if location_name == "Cardinal Towne (CLOSED TEMPORARILY)":
            item = items[i + 2]

        raw_data = (
            str(item)
            .replace("<p>", "")
            .replace("</p>", "")
            .replace("\n", "")
            .split("<br/>")
        )

        street_address = raw_data[-2][: raw_data[-2].find(",")].strip()
        city = raw_data[-2][
            raw_data[-2].find(",") + 1 : raw_data[-2].rfind(",")
        ].strip()
        state = raw_data[-2][
            raw_data[-2].rfind(",") + 1 : raw_data[-2].rfind(" ")
        ].strip()
        zip_code = raw_data[-2][raw_data[-2].rfind(" ") + 1 :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = raw_data[-1].strip()
        location_type = "<MISSING>"

        for mp in maps:
            if location_name[:6] in str(mp):
                latitude = mp["data-lat"]
                longitude = mp["data-lng"]
        try:
            int(latitude[4:8])
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
