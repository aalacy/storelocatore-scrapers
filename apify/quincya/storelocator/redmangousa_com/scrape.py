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

    base_link = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=TXEJGBXGVEQUABKM&multi_account=false&pageSize=100"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    data = []
    found = []
    locator_domain = "redmangousa.com"

    for store in stores:
        store = store["store_info"]
        location_name = store["name"]
        if "Permanently Closed" in location_name:
            continue
        street_address = store["address"].strip()
        city = store["locality"]
        state = store["region"]
        if not state:
            continue
        zip_code = store["postcode"]
        country_code = store["country"]
        store_number = store["corporate_id"]
        location_type = store["status"]
        phone = store["phone"]
        hours_of_operation = (
            store["store_hours"]
            .replace("0,", "0-")
            .replace("1,", "Mon ")
            .replace("2,", "Tue ")
            .replace("3,", "Wed ")
            .replace("4,", "Thu ")
            .replace("5,", "Fri ")
            .replace("6,", "Sat ")
            .replace("7,", "Sun ")
        )[:-1]
        if "Mon" not in hours_of_operation:
            hours_of_operation = hours_of_operation + ";Mon Closed"
        if "Sat" not in hours_of_operation:
            hours_of_operation = hours_of_operation + ";Sat Closed"
        if "Sun" not in hours_of_operation:
            hours_of_operation = hours_of_operation + ";Sun Closed"
        if not hours_of_operation or "close" in location_type:
            hours_of_operation = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        link = store["website"]
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
