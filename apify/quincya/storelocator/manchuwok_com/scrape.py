import csv

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

    base_link = "https://manchuwok.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t=1612506673105"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    found_poi = []

    items = base.find_all("item")

    locator_domain = "manchuwok.com"
    for item in items:
        location_name = BeautifulSoup(item.location.text, "lxml").get_text(" ").strip()
        if "closed" in location_name.lower():
            continue

        raw_address = item.address.text.strip().split("  ")

        street_address = BeautifulSoup(raw_address[0], "lxml").get_text(" ").strip()
        if street_address in found_poi:
            continue
        found_poi.append(street_address)

        city = raw_address[1].replace(",", "").strip()
        state = raw_address[2].split()[0].strip()
        if len(state) > 3:
            continue
        zip_code = raw_address[2].strip()[3:].strip()
        if len(zip_code) > 7:
            continue
        if not zip_code:
            zip_code = "<MISSING>"
        if len(zip_code) < 5:
            continue

        if " " in zip_code:
            country_code = "CA"
        else:
            country_code = "US"

        store_number = item.storeid.text.strip()
        location_type = "<MISSING>"
        phone = "<MISSING>"

        latitude = item.latitude.text.strip()
        longitude = item.longitude.text.strip()

        try:
            hours_of_operation = (
                BeautifulSoup(item.operatinghours.text, "lxml").get_text(" ").strip()
            )
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
        except:
            hours_of_operation = "<MISSING>"

        data.append(
            [
                locator_domain,
                "https://manchuwok.com/locations/",
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
