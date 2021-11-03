import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("myvue_com")


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

    base_link = "https://www.myvue.com/data/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    main_headers = {
        "User-Agent": user_agent,
        "Referer": "https://www.myvue.com/cinema/glasgow-st-enoch/whats-on",
        "X-Requested-With": "XMLHttpRequest",
    }
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    items = session.get(base_link, headers=main_headers).json()["venues"]

    fond_gps = []
    locator_domain = "myvue.com"

    for row in items:
        stores = row["cinemas"]
        for store in stores:
            link = (
                "https://www.myvue.com/cinema/" + store["link_name"] + "/getting-here"
            )
            link = link.replace("bury-the rock", "bury-the-rock")
            logger.info(link)
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            location_name = base.find(class_="select-cinema__wrapper").text.strip()

            try:
                raw_address = (
                    base.find(class_="container container--scroll")
                    .div.text.strip()
                    .split("\n")
                )
            except:
                continue
            street_address = raw_address[-3].split(",")[0].strip()
            try:
                street_address = (
                    raw_address[-4].strip() + " " + street_address
                ).strip()
            except:
                pass
            state = "<MISSING>"
            city = raw_address[-2].strip()
            zip_code = raw_address[-1].strip()
            country_code = "GB"

            store_number = store["id"]
            location_type = "<MISSING>"
            phone = "<MISSING>"

            hours_of_operation = "<MISSING>"

            if "cinema is closed at the moment" in base.text:
                location_type = "Temporarily Closed"
            try:
                if (
                    "venue is opening on"
                    in base.find(class_="cmv-message__message").text
                ):
                    location_type = (
                        base.find(class_="cmv-message__message")
                        .text.split(".")[0]
                        .strip()
                    )
            except:
                pass

            geo = (
                base.find("a", string="Get directions")["href"].split("=")[1].split(",")
            )
            latitude = geo[0]
            longitude = geo[1]
            lat_long = latitude + "_" + longitude
            if lat_long in fond_gps:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            else:
                fond_gps.append(lat_long)

            yield [
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
