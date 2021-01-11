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

    base_link = "https://storerocket.global.ssl.fastly.net/api/user/6wgpr528XB/locations?radius=100&units=miles"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["results"]["locations"]

    data = []
    found = []
    locator_domain = "ribcrib.com"

    for store in stores:
        location_name = store["name"]
        try:
            street_address = (
                store["address_line_1"] + " " + store["address_line_2"]
            ).strip()
        except:
            street_address = store["address_line_1"].strip()

        if not street_address[:1].isdigit():
            street_address = store["display_address"].split(",")[0]

        city = store["city"]
        state = store["state"]
        zip_code = store["postcode"]
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        hours_of_operation = ""
        raw_hours = store["hours"]
        for hour in raw_hours:
            hours_of_operation = (
                hours_of_operation + " " + hour + " " + raw_hours[hour]
            ).strip()
        latitude = store["lat"]
        longitude = store["lng"]
        link = "https://ribcrib.com/locations/?location=" + store["slug"]
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
