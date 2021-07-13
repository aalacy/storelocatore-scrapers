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

    base_link = "https://www.wagamama.us/restaurants/index.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    all_links = []

    locator_domain = "wagamama.us"

    main_links = base.find_all(class_="Directory-listLink")

    for main_link in main_links:
        next_link = "https://www.wagamama.us/restaurants/" + main_link["href"]
        req = session.get(next_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find_all(class_="Teaser-cta")

        for item in items:
            all_links.append("https://www.wagamama.us/restaurants/" + item["href"])

    for link in all_links:
        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")

        location_name = "Wagamama " + item.h1.text.title()
        try:
            street_address = (
                item.find(class_="c-address-street-1").text.title()
                + " "
                + item.find(class_="c-address-street-2").text.title()
            )
        except:
            street_address = item.find(class_="c-address-street-1").text.title()
        street_address = street_address.replace("Quincy Market Building", "").strip()
        city = item.find(class_="c-address-city").text.title()
        state = item.find(class_="c-address-state").text.upper()
        zip_code = item.find(class_="c-address-postal-code").text.strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = item.find(id="phone-main").text.strip()
        latitude = item.find("meta", attrs={"itemprop": "latitude"})["content"]
        longitude = item.find("meta", attrs={"itemprop": "longitude"})["content"]
        location_type = "<MISSING>"
        hours_of_operation = " ".join(
            list(item.find(class_="c-hours-details").tbody.stripped_strings)
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
