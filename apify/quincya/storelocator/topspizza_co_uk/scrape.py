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

    base_link = "https://topspizza.co.uk/rest/stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    store_data = session.post(base_link, headers=headers).json()

    data = []
    for store in store_data:
        final_link = "https://topspizza.co.uk/" + store["nickname"]
        locator_domain = "topspizza.co.uk"

        location_name = store["name"]
        city = store["city"].strip().title()
        street_address = store["address"].strip().split(city)[0].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1].strip()
        state = "<MISSING>"
        zip_code = store["postcode"]
        country_code = "GB"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["tel"]

        hours_of_operation = (
            "Mon: "
            + store["Monday"]
            + " Tue: "
            + store["Tuesday"]
            + " Wed: "
            + store["Wednesday"]
            + " Thu: "
            + store["Thursday"]
            + " Fri: "
            + store["Friday"]
            + " Sat: "
            + store["Saturday"]
            + " Sun: "
            + store["Sunday"]
        ).strip()

        latitude = store["latitude"]
        longitude = store["longitude"]

        data.append(
            [
                locator_domain,
                final_link,
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
