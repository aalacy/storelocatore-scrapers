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

    base_link = "https://republicebank.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "republicebank.com"

    items = (
        base.find(class_="page-content")
        .find_all(class_="wpv-grid")[0]
        .find_all(class_="wpv-grid")[2:]
    )
    for item in items:
        raw_data = list(item.stripped_strings)
        location_name = "<MISSING>"
        raw_address = raw_data[0].split(",")
        street_address = "".join(raw_address[:-1])
        city = raw_address[-1][:-6].strip()
        state = "IL"
        zip_code = raw_address[-1][-6:].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = raw_data[1].split("f")[0].replace("p", "").replace("Retail", "").strip()
        location_type = "<MISSING>"
        latitude = "<INACCESSIBLE>"
        longitude = "<INACCESSIBLE>"

        hours_of_operation = ""
        for i, row in enumerate(raw_data):
            if "lobby hours" in row.lower():
                break
        for y in range(5):
            text = raw_data[y + i + 1]
            if "day" in text.lower():
                hours_of_operation = (hours_of_operation + " " + text).strip()
            else:
                break

        data.append(
            [
                locator_domain,
                base_link,
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
