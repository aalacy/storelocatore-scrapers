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

    base_link = "https://www.dollar.com/loc/modules/multilocation/?near_location=US&services__in=&published=1&within_business=true&limit=500"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["objects"]

    data = []
    found = []
    locator_domain = "dollar.com"

    for store in stores:
        location_name = store["location_name"]
        try:
            street_address = (store["street"] + " " + store["street2"]).strip()
        except:
            street_address = store["street"].strip()
        if " CLOSE " in street_address.upper():
            continue
        city = store["geocoded"].split(",")[-3].strip()
        state = store["state"]
        if not state:
            state = "<MISSING>"
        zip_code = store["postal_code"]
        country_code = store["country"]
        store_number = store["id"]
        location_type = "<MISSING>"
        try:
            phone = store["phonemap"]["phone"]
        except:
            phone = "<MISSING>"
        hours_of_operation = ""
        raw_hours = store["formatted_hours"]["primary"]["days"]
        for hour in raw_hours:
            hours_of_operation = (
                hours_of_operation + " " + hour["label"] + " " + hour["content"]
            ).strip()
        latitude = store["lat"]
        longitude = store["lon"]
        link = store["location_url"].replace(
            "test.dollar.com", "https://www.dollar.com"
        )
        if link in found:
            continue
        found.append(link)
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
