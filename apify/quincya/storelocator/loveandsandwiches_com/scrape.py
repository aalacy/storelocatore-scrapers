import csv

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("ikessandwich.com")


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

    base_link = "https://locations.ikessandwich.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "ikessandwich.com"

    items = base.find(id="browse-content").find_all(class_="ga-link")

    for item in items:
        state_link = item["href"]
        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        stores = base.find(class_="map-list-wrap map-list-tall").ul.find_all(
            "li", recursive=False
        )
        for store in stores:
            store = store.find(class_="map-list-item")
            location_name = store.a.text.strip()
            link = store.a["href"]
            log.info(link)

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            if "coming soon" in base.find(class_="map-list").text.lower():
                continue

            street_address = (
                base.find(class_="address").find_all("span")[-2].text.strip()
            )
            city_line = (
                base.find(class_="address").find_all("span")[-1].text.strip().split(",")
            )
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = base.find(class_="map-list").div["data-fid"]
            map_link = base.find(class_="ga-link")["href"]
            latitude = map_link.split("=")[-1].split(",")[0]
            longitude = map_link.split("=")[-1].split(",")[1]
            location_type = ", ".join(
                list(base.find(class_="location-services").stripped_strings)
            )

            phone = base.find(class_="phone ga-link").text.strip()
            hours_of_operation = " ".join(
                list(base.find(class_="hours").stripped_strings)
            )

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
