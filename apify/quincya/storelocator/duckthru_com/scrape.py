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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.duckthru.com/wp-admin/admin-ajax.php?action=store_search&lat=36.28682&lng=-76.98468&max_results=100&search_radius=100&autoload=1"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    data = []
    locator_domain = "duckthru.com"

    for store in stores:
        location_name = store["store"]
        street_address = store["address"].strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = store["country"]
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        if not phone:
            phone = "<MISSING>"
        try:
            hours_of_operation = BeautifulSoup(store["hours"], "lxml").get_text(" ")
        except:
            hours_of_operation = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]
        link = store["permalink"]
        # Store data
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
