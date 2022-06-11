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

    base_link = "https://www.wickes.co.uk/store-finder"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = items = base.find(id="storeSelectList").find_all("option")[1:]
    locator_domain = "wickes.co.uk"

    for item in items:
        store_number = item["value"]
        link = "https://www.wickes.co.uk/store/" + store_number
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.upper().strip()
        street_address = (
            base.find(class_="card-store__name").text.strip()
            + " "
            + base.find(class_="card-store__location").text.strip()
        )
        city = base.find(class_="card-store__city").text.strip()
        state = "<MISSING>"
        zip_code = base.find(class_="card-store__postcode").text.strip()
        country_code = "UK"
        location_type = "<MISSING>"
        phone = base.find(class_="card-store__tel").a.text.strip()
        if not phone:
            phone = "<MISSING>"
        if "temporarily closed" in base.text:
            location_type = "Temporarily Closed"

        try:
            hours_of_operation = (
                " ".join(
                    list(
                        base.find_all(class_="card-store__info-block")[
                            1
                        ].stripped_strings
                    )
                )
                .replace("Standard opening times", "")
                .strip()
                .replace("Mon - Tue - Wed - Thu - Fri - Sat - Sun -", "<MISSING>")
            )
        except:
            hours_of_operation = "<MISSING>"

        latitude = base.find(class_="btn btn-primary btn-navigate-to")["data-latitude"]
        longitude = base.find(class_="btn btn-primary btn-navigate-to")[
            "data-longitude"
        ]

        if latitude == "0.0":
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
