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

    base_link = "https://www.deserres.ca/apps/deserres/stores?lang=en_ca"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    data = []
    locator_domain = "deserres.ca"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["stores"]

    for store in stores:
        location_name = store["name"].strip()
        link = "https://www.deserres.ca/pages/" + store["page_handle"]

        raw_address = store["address"]
        try:
            street_address = (
                raw_address["address1"] + " " + raw_address["address2"]
            ).strip()
        except:
            street_address = raw_address["address1"]
        city = raw_address["city"]
        state = raw_address["province"]
        zip_code = raw_address["postal_code"]
        country_code = "CA"
        store_number = store["store_id"]
        phone = raw_address["phone"]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        hours = ""
        raw_hours = store["opening_hours"]
        for raw_hour in raw_hours:
            try:
                clean_hours = raw_hour["open"] + "-" + raw_hour["close"]
            except:
                clean_hours = "Closed"
            hours = (hours + " " + raw_hour["day"] + " " + clean_hours).strip()
        hours = hours.replace("  ", " ")

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
                hours,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
