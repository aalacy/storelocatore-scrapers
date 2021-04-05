import csv

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://store.fastretailing.com/api/uk/uniqlo/200/getStoreList.json?lang=english&r=storelocator&sort=%2Bpostcode"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["result"]["stores"]

    data = []
    locator_domain = "uniqlo.com"

    for store in stores:
        location_name = store["store_name"]
        street_address = store["number"].split(", London")[0].strip()
        city = store["municipality"].strip()
        state = "<MISSING>"
        zip_code = store["postcode"]
        country_code = "UK"
        store_number = store["store_id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        if not phone:
            phone = "<MISSING>"

        if "temporarily closed" in store["open_hours"]:
            hours_of_operation = "Temporarily Closed"
        else:
            hours_of_operation = (
                (
                    "Mon "
                    + store["mon_open_at"]
                    + "-"
                    + store["mon_close_at"]
                    + " Tue "
                    + store["tue_open_at"]
                    + "-"
                    + store["tue_close_at"]
                    + " Wed "
                    + store["wed_open_at"]
                    + "-"
                    + store["wed_close_at"]
                    + " Thu "
                    + store["thu_open_at"]
                    + "-"
                    + store["thu_close_at"]
                    + " Fri "
                    + store["fri_open_at"]
                    + "-"
                    + store["fri_close_at"]
                    + " Sat "
                    + store["sat_open_at"]
                    + "-"
                    + store["sat_close_at"]
                    + " Sun "
                    + store["sun_open_at"]
                    + "-"
                    + store["sun_close_at"]
                )
                .replace("Mon -", "")
                .replace("Tue -", "")
                .replace("Wed -", "")
                .replace("Thu -", "")
                .replace("Fri -", "")
                .replace("Sat -", "")
                .replace("Sun -", "")
                .strip()
            )

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        latitude = store["lat"]
        longitude = store["lon"]
        link = "https://map.uniqlo.com/uk/en/detail/" + str(store_number)
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
