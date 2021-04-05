import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    locator_domain = "https://www.stayaka.com/"
    ext = "locations"

    response = session.get(locator_domain + ext, headers=headers)

    soup = BeautifulSoup(response.content, "html.parser")

    link_list = []
    main = soup.find(class_="submenu level-2 destinations")
    links = main.find_all("a")
    for link in links:
        if "aka" not in link["href"]:
            continue
        if "http" not in link["href"]:
            l = locator_domain + link["href"][1:]
        else:
            l = link["href"]
        link_list.append(l)

    all_store_data = []
    for link in link_list:
        response = session.get(link, headers=headers)

        soup = BeautifulSoup(response.content, "html.parser")
        cont = json.loads(soup.find("script", {"type": "application/ld+json"}).text)
        location_name = cont["name"]
        page_url = cont["url"]

        phone_number = cont["telephone"]
        addy = cont["address"]
        street_address = addy["streetAddress"].replace("Cira Centre South,", "").strip()

        city = addy["addressLocality"]
        state = addy["addressRegion"]
        zip_code = addy["postalCode"]
        country_code = addy["addressCountry"]

        if state == "London":
            country_code = "GB"

        lat = cont["geo"]["latitude"]
        longit = cont["geo"]["longitude"]
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours = "<MISSING>"

        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            page_url,
        ]

        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
