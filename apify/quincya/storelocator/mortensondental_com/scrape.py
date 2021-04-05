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

    base_link = "https://mortensondental.com/wp-content/plugins/mdp-connect/data/mdpConnect_mortensondental.com_locations.json"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    data = []

    locator_domain = "mortensondental.com"

    for store in stores:
        location_name = store["name"].strip()
        link = store["web"]
        street_address = store["address"].strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["postal"]
        country_code = "US"
        store_number = store["id"]
        phone = store["phone"]
        latitude = store["lat"]
        longitude = store["lng"]

        hours_of_operation = ""
        raw_hours = store["hours"]
        for hours in raw_hours:
            day = hours["day"]
            opens = hours["begin"]
            closes = hours["end"]
            if opens != "" and closes != "":
                clean_hours = day + " " + opens + "-" + closes
            else:
                clean_hours = day + " Closed"
            hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

        location_type = "<MISSING>"

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
