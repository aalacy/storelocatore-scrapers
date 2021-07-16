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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    data = []
    locator_domain = "cardenasmarkets.com"

    store_link = "https://locations.cardenasmarkets.com/modules/multilocation/?business_id=472225&limit=500&published=1&threshold=20000&near_location=CA&services__in="

    stores = session.get(store_link, headers=headers).json()["objects"]

    for store in stores:
        location_name = store["location_name"].split(",")[0].strip()
        street_address = store["street"].strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["postal_code"]
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phones"][0]["number"]
        latitude = store["lat"]
        longitude = store["lon"]
        link = store["location_url"]

        hours_of_operation = ""
        raw_hours = store["formatted_hours"]["primary"]["days"]
        for hours in raw_hours:
            day = hours["label"]
            clean_hours = day + " " + hours["content"]
            hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

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
