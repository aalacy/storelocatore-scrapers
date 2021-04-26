import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

log = SgLogSetup().get_logger("dakotawatch.com")


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

    session = SgRequests()

    data = []
    found = []

    main_link = "https://dakotawatch.com/"

    req = session.get(main_link)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "stores.js?shop=" in str(script):
            script = str(script)
            shopid = script.split("=")[-1].split('"')[0]
            break

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "SameSite=None",
        "Origin": "https://findastore.appdevelopergroup-pack1.co",
        "Referer": "https://findastore.appdevelopergroup-pack1.co/embed/" + shopid,
        "DNT": "1",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "X-Requested-With": "XMLHttpRequest",
    }

    coords = static_coordinate_list(radius=20, country_code=SearchableCountries.USA)

    base_link = "https://findastore.appdevelopergroup-pack1.co/findastore"

    log.info("Running sgzips ..can take an hour ..")

    for lat, lng in coords:

        payload = {
            "lat": lat,
            "lng": lng,
            "shopid": shopid,
        }

        try:
            stores = session.post(base_link, headers=headers, data=payload).json()[
                "stores"
            ]
        except:
            session = SgRequests()
            stores = session.post(base_link, headers=headers, data=payload).json()[
                "stores"
            ]

        for store in stores:
            locator_domain = "dakotawatch.com"
            location_name = store["name"].strip()
            raw_data = store["address"].split(",")
            street_address = raw_data[0].replace("  ", " ").strip()
            city = raw_data[1].strip()
            state = raw_data[2].strip()
            zip_code = raw_data[3].strip()
            country_code = "US"
            store_number = store["id"]
            phone = store["phone"].strip()
            if "N/A" in phone:
                phone = "<MISSING>"
            if store_number in found:
                continue
            found.append(store_number)
            location_type = "<MISSING>"
            latitude = store["lat"]
            longitude = store["lng"]
            hours_of_operation = "<MISSING>"
            link = "<MISSING>"

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
