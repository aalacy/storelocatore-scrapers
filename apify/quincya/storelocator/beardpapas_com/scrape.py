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

    base_link = "https://www.beardpapas.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find(class_="col sqs-col-12 span-12").find_all(
        class_="sqs-block html-block sqs-block-html"
    )
    locator_domain = "beardpapas.com"

    for item in items:
        if "beard papa" not in item.text.lower():
            continue

        raw_data = list(item.stripped_strings)

        location_name = raw_data[0].strip()
        street_address = raw_data[1].strip()
        if "Located in" in street_address:
            street_address = raw_data[2].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city = raw_data[-1].split(",")[0].strip()
        state = raw_data[-1].split(",")[1].split()[0].strip()
        try:
            zip_code = raw_data[-1].split(",")[1].split()[1].strip()
        except:
            if "2167 Broadway" in street_address:
                street_address = "2167 Broadway"
                city = "New York"
                state = "NY"
                zip_code = "10024"
            else:
                zip_code = raw_data[2].split(",")[2].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
