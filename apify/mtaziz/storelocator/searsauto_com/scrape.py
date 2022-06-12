import csv
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import sglog

session = SgRequests()

base_url = "https://www.searsauto.com"
log = sglog.SgLogSetup().get_logger(logger_name=base_url)


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    MAX_RESULTS = None
    MAX_DISTANCE = 200
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-type": "application/json",
        "origin": "https://www.searsauto.com",
        "referer": "https://www.searsauto.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    }
    unique_rows = []
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=MAX_DISTANCE,
        max_search_results=MAX_RESULTS,
    )
    maxZ = search.items_remaining()
    total = 0
    for zip_code in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        found = 0
        r = session.post("https://app.searsauto.com/sa-api/init", headers=headers)
        location_url = f"https://app.searsauto.com/sa-api/stores/{str(zip_code)}"
        r = session.get(location_url, headers=headers)
        r.raise_for_status()
        r_json = r.json()
        json_data = r_json["autoStores"]
        if json_data:
            for value in json_data:
                locator_domain = base_url if base_url else "<MISSING>"
                location_name = "Sears Auto Center at " + value["city"]
                location_name = location_name if location_name else "<MISSING>"
                street_address = value["address1"] + " " + value["address2"].strip()
                street_address = street_address if street_address else "<MISSING>"
                city = value["city"] if value["city"] else "<MISSING>"
                state = value["state"] if value["state"] else "<MISSING>"
                country_code = "US"
                zip = value["postalCode"] if value["postalCode"] else "<MISSING>"
                store_number = (
                    value["storeNumber"] if value["storeNumber"] else "<MISSING>"
                )
                phone = value["phone"] if value["phone"] else "<MISSING>"
                location_type = value["storeType"] + " - " + value["locationType"]
                latitude = value["latitude"] if value["latitude"] else "<MISSING>"
                longitude = value["longitude"] if value["longitude"] else "<MISSING>"
                hoo = value["hours"]
                hours_of_operation = []
                for j in hoo:
                    if "open" in j:
                        timedate = j["dayOfWeek"] + " " + j["open"] + "-" + j["close"]
                        hours_of_operation.append(timedate.lower())

                hours_of_operation = (
                    "; ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
                )
                page_url = "https://www.searsauto.com" + value["detailsUrl"]
                search.found_location_at(
                    value["latitude"],
                    value["longitude"],
                )

                row = [
                    locator_domain,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                    page_url,
                ]
                row = [
                    x.encode("ascii", "ignore").decode("ascii").strip()
                    if type(x) == str
                    else x
                    for x in row
                ]
                if row not in unique_rows:
                    unique_rows.append(row)
                    found += 1
        total += found
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        log.info(f"{zip_code} | found: {found} | total: {total} | progress: {progress}")

    return unique_rows


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
