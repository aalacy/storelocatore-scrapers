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

    base_link = "https://local.safeway.com/pak-n-save/ca.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="Directory-listLink")
    locator_domain = "https://local.safeway.com"

    for i in items:
        link = locator_domain + i["href"].split("..")[1]

        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")

        location_name = item.h1.text.strip()
        street_address = item.find(class_="c-address-street-1").text.strip()
        city = item.find(class_="c-address-city").text.strip()
        state = item.find(class_="c-address-state").text.strip()
        zip_code = item.find(class_="c-address-postal-code").text.strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.find(id="phone-main").text.strip()
        hours_of_operation = " ".join(
            list(item.find(class_="c-hours-details").tbody.stripped_strings)
        )
        latitude = item.find("meta", attrs={"itemprop": "latitude"})["content"]
        longitude = item.find("meta", attrs={"itemprop": "longitude"})["content"]

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
