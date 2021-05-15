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

    base_link = "https://www.club4fitness.com/location/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "club4fitness.com"

    items = base.find_all("article")

    for i in items:
        location_name = i.a.text
        if "opening soon" in location_name.lower():
            continue
        link = i.a["href"]
        req = session.get(link, headers=headers)
        item = BeautifulSoup(req.text, "lxml")

        raw_address = (
            i.find(class_="elementor-text-editor")
            .text.replace(", Suite", " Suite")
            .replace(", USA", "")
            .replace("Ridgeland", ", Ridgeland")
            .split(",")
        )
        street_address = raw_address[0]
        city = raw_address[1].strip()
        if len(raw_address) == 4:
            state = raw_address[2]
            zip_code = raw_address[3]
        if len(raw_address) == 3:
            state = raw_address[-1].split()[0]
            zip_code = raw_address[-1].split()[1]
        country_code = "US"
        store_number = i["id"].split("-")[1]
        phone = (
            item.main.find(class_="elementor-button-text")
            .text.replace("Call", "")
            .strip()
        )
        location_type = "<MISSING>"
        hours_of_operation = " ".join(
            list(item.find(class_="dce-acf-repater-list").stripped_strings)
        )
        latitude = "<INACCESSIBLE>"
        longitude = "<INACCESSIBLE>"

        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state.strip(),
                zip_code.strip(),
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
