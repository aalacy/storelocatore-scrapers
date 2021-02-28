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

    base_link = "https://dionsquikchik.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="type3 icon-section")
    locator_domain = "dionsbest.com"

    for item in items:

        raw_data = list(item.stripped_strings)

        location_name = raw_data[0].strip()
        street_address = raw_data[1].strip()
        city = raw_data[2].split(",")[0].strip()
        state = raw_data[2].split(",")[1].split()[0].strip()
        zip_code = raw_data[2].split()[-1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = raw_data[4].strip()
        if "-" not in phone:
            phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        try:
            hours_of_operation = raw_data[5].strip()
        except:
            if "temporarily" in item.text.lower():
                hours_of_operation = "Closed Temporarily"
            else:
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
