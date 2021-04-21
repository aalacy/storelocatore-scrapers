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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    data = []
    locator_domain = "winndixie.com"

    store_link = "https://www.winndixie.com/V2/storelocator/getStores?search=jacksonville,%20fl&strDefaultMiles=1000&filter="

    stores = session.get(store_link, headers=headers).json()

    for store in stores:
        if "winn dixie" not in store["StoreBannerTypDesc"].lower():
            continue
        location_name = store["StoreName"]
        street_address = store["Address"]["AddressLine2"].strip()
        if not location_name:
            location_name = "Winn-Dixie At " + street_address
        city = store["Address"]["City"]
        state = store["Address"]["State"]
        zip_code = store["Address"]["Zipcode"]
        country_code = "US"
        store_number = store["StoreCode"]
        location_type = store["Location"]["LocationTypeDescription"]
        phone = store["Phone"]
        hours_of_operation = store["WorkingHours"].strip()
        latitude = store["Address"]["Latitude"]
        longitude = store["Address"]["Longitude"]
        link = "https://www.winndixie.com/storedetails?search=" + str(
            store["StoreCode"]
        )
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

    fuel_link = "https://www.winndixie.com/V2/storelocator/getFuelStores"

    js = {"search": "jacksonville, fl", "strDefaultMiles": "200"}
    fuel_stores = session.post(fuel_link, headers=headers, json=js).json()["locations"]
    for store in fuel_stores:
        location_name = store["name"]
        street_address = store["address"]["street1"].strip()
        city = store["address"]["city"]
        state = store["address"]["stateCode"]
        zip_code = store["address"]["zipCode"]
        country_code = "US"
        store_number = str(int(store["id"]))
        location_type = "Fuel"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]
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
