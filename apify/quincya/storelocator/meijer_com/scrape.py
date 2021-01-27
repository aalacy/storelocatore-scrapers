import csv

from sglogging import SgLogSetup

from sgrequests import SgRequests

log = SgLogSetup().get_logger("meijer.com")


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
    end = False
    locator_domain = "meijer.com"
    for page_num in range(50):
        base_link = (
            "https://www.meijer.com/shop/en/store-finder/search?q=60010&page=%s&radius=4500"
            % page_num
        )

        log.info(base_link)

        for i in range(5):
            stores = session.get(base_link, headers=headers).json()["data"]
            if len(stores) == 0:
                if page_num < 30:
                    continue
                else:
                    end = True
                    break
            else:
                break
        if not end:
            for store in stores:
                location_name = store["displayName"]
                street_address = (store["line1"] + " " + store["line2"]).strip()
                city = store["town"]
                state = store["state"]
                zip_code = store["postalCode"]
                country_code = "US"
                store_number = store["name"]
                location_type = "<MISSING>"
                phone = store["phone"]
                hours_of_operation = "<INACCESSIBLE>"
                latitude = store["latitude"]
                longitude = store["longitude"]
                link = "https://www.meijer.com/shop/en/store/" + store_number
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
        else:
            break
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
