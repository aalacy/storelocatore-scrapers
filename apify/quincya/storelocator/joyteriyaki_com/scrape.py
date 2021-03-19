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

    base_link = "https://www.joyteriyaki.com/our_locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    names = []
    locs = []

    items = base.find(id="Containerc9tk").find_all(class_="font_7")
    for item in items:
        if "Joy Teriyaki" in item.text:
            names.append(item)
        else:
            locs.append(item)

    locator_domain = "joyteriyaki.com"

    for i in range(len(names)):

        location_name = (
            names[i].text.encode("ascii", "replace").decode().replace("?", " ").strip()
        )

        raw_address = locs[i].text.replace("\xa0", " ").strip()

        street_address = (
            " ".join(raw_address[: raw_address.rfind(",")].split()[:-1])
            .replace("104,", "104")
            .strip()
        )
        city = raw_address[: raw_address.rfind(",")].split()[-1].strip()

        if city == "Linn":
            street_address = street_address.split(",")[0]
            city = "West Linn"

        state = raw_address.split(",")[-1].split()[0].strip()
        zip_code = raw_address.split(",")[-1].split()[1].strip()

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = raw_address.split("Tel")[-1].strip()
        if "(" not in phone:
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
