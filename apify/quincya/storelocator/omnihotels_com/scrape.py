import csv

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

    base_link = "https://www.omnihotels.com/api/sitecore/property/getproperties"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    data = []

    locator_domain = "omnihotels.com"

    for store in stores:
        if store["comingSoon"]:
            continue
        link = "https://www.omnihotels.com" + store["link"]
        if "cancun" in link:
            continue
        location_name = store["name"]
        street_address = store["address"].split("(")[0].strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["zipCode"]
        country_code = "US"
        if len(zip_code) > 5:
            country_code = "CA"

        store_number = store["code"]
        phone = store["phoneNumber"]
        hours_of_operation = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]

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
                "<MISSING>",
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
