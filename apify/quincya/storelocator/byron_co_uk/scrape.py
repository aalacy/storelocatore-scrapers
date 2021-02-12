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

    base_link = "https://www.byron.co.uk/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="image-card sqs-dynamic-text-container")
    locator_domain = "byron.co.uk"

    for item in items:
        location_name = item.p.text.strip()
        location_type = item.find_all("p")[2].text.strip()
        raw_address = item.find_all("p")[3].text.strip()
        if ", " in location_type:
            raw_address = item.find_all("p")[2].text.strip()
            location_type = item.find_all("p")[1].text.strip()
        zip_code = raw_address.split()[-1]
        if len(zip_code) < 5:
            zip_code = " ".join(raw_address.split()[-2:])
        raw_address = raw_address[: raw_address.rfind(zip_code)].strip()
        city = raw_address.split()[-1]
        street_address = raw_address[: raw_address.rfind(city)].strip()

        if city == "Edmunds":
            city = "Bury St Edmunds"
            street_address = street_address.replace("Bury St", "").strip()

        if city == "Keynes":
            city = "Milton Keynes"
            street_address = street_address.replace("Milton", "").strip()

        if street_address[-1:] == ",":
            street_address = street_address[:-1].strip()
        state = "<MISSING>"
        store_number = "<MISSING>"
        country_code = "GB"
        try:
            phone = item.a.text.strip()
        except:
            phone = item.span.text
        hours_of_operation = " ".join(list(item.ul.stripped_strings))

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        data.append(
            [
                locator_domain,
                "https://www.byron.co.uk/locations",
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
