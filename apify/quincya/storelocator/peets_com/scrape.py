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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []
    locator_domain = "peets.com"

    base_link = "https://api.momentfeed.com/v1/analytics/api/v2/llp/sitemap?auth_token=CVVDLCJRQEBHCLCL&country=US&multi_account=false"

    stores = session.get(base_link, headers=headers).json()["locations"]

    for store in stores:
        street_address = store["store_info"]["address"].strip()
        city = store["store_info"]["locality"]
        state = store["store_info"]["region"]
        zip_code = store["store_info"]["postcode"]
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        country_code = store["store_info"]["country"]
        location_type = store["open_or_closed"]

        url = (
            "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=CVVDLCJRQEBHCLCL&address="
            + street_address.replace(" ", "+")
            + "&locality="
            + city
            + "&multi_account=false&pageSize=30&region="
            + state
        )

        link = "https://locations.peets.com" + store["llp_url"]

        base_js = session.get(url, headers=headers).json()[0]["store_info"]
        location_name = base_js["name"] + " " + city

        if "permanently closed" in location_name.lower():
            continue

        street_address = (street_address + " " + base_js["address_extended"]).strip()
        store_number = base_js["corporate_id"]
        latitude = base_js["latitude"]
        longitude = base_js["longitude"]
        phone = base_js["phone"]
        raw_hours = base_js["store_hours"]
        if "close" in location_type.lower():
            hours_of_operation = location_type.title()
        else:
            hours_of_operation = (
                raw_hours.replace("1,", "Monday ")
                .replace(";2,", " Tuesday ")
                .replace(";3,", " Wednesday ")
                .replace(";4,", " Thursday ")
                .replace(";5,", " Friday ")
                .replace(";6,", " Saturday ")
                .replace(";7,", " Sunday ")
                .replace("0;", "0")
                .replace(",", "-")
            )

            if "Saturday" not in hours_of_operation:
                hours_of_operation = hours_of_operation + " Saturday Closed"

            if "Sunday" not in hours_of_operation:
                hours_of_operation = hours_of_operation + " Sunday Closed"

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
