import csv

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

    base_link = "https://www.wagamama.us/restaurants"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    locator_domain = "wagamama.us"

    items = base.find(class_="restaurant-hub__results-list").find_all("li")

    for item in items:

        location_name = "Wagamama " + item.h2.text.title()
        raw_address = list(item.find(class_="restaurant-hub__address").stripped_strings)
        street_address = (
            " ".join(raw_address[:-3])
            .title()
            .replace("Quincy Market Building", "")
            .strip()
        )
        city = raw_address[-3].title()
        state = raw_address[-2].upper()
        zip_code = raw_address[-1].title()
        country_code = "US"
        store_number = item["data-id"]
        phone = item.find(class_="restaurant-hub__phone").text.strip()
        latitude = item["data-lat"]
        longitude = item["data-lng"]

        link = "https://www.wagamama.us" + item.find_all("a")[-1]["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        location_type = "<MISSING>"
        hours_of_operation = " ".join(
            list(
                base.find(
                    class_="restaurant-find-us__opening-times-inner"
                ).table.stripped_strings
            )
        )

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
