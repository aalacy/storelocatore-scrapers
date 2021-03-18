import csv

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://api-2.freshop.com/1/stores?app_key=kings_county_market&has_address=true&limit=-1&token=434265630f02f0db1199faac7565cbef"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["items"]

    data = []
    locator_domain = "kingscountymarket.com"

    for store in stores:
        location_name = store["name"]
        street_address = store["address_1"]
        city = store["city"]
        state = store["state"]
        zip_code = store["postal_code"]
        country_code = "US"
        store_number = store["store_number"]
        location_type = "<MISSING>"
        phone = store["phone_md"].split("\n")[0].strip()
        hours_of_operation = store["hours_md"].replace("\n", " ").strip()
        latitude = store["latitude"]
        longitude = store["longitude"]
        link = store["url"]

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
