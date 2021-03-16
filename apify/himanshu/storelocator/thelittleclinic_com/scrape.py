import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="thelittleclinic.com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    zip_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=100,
        max_radius_miles=200,
    )
    adressess = []

    for i, zip_code in enumerate(zip_codes):

        log.info(
            "Searching: %s | Items remaining: %s"
            % (zip_code, zip_codes.items_remaining())
        )

        link = (
            "https://www.thelittleclinic.com/appointment-management/v1/clinics?filter.businessName=tlc&filter.freeFormAddress=%s&filter.maxResults=100&page.size=500"
            % zip_code
        )
        r = session.get(
            link,
            headers=headers,
        )
        json_data = r.json()
        j = json_data["data"]["clinics"]

        for i in j:
            store = []
            store.append("https://www.thelittleclinic.com/")
            store.append(i["name"])
            store.append(" ".join(i["address"]["addressLines"]))
            if store[2] in adressess:
                continue
            adressess.append(store[2])
            store.append(i["address"]["cityTown"])
            store.append(i["address"]["stateProvince"])
            store.append(i["address"]["postalCode"])
            store.append("US")
            store.append(i["id"])
            try:
                phone = i["phone"]
            except:
                phone = "<MISSING>"
            store.append(phone)
            if i["isSchedulerEnabled"]:
                loc_type = "Scheduling Appointments Available"
            else:
                loc_type = "Scheduling Appointments Currently Unavailable"
            store.append(loc_type)
            lat = i["location"]["lat"]
            lng = i["location"]["lng"]
            store.append(lat)
            store.append(lng)
            zip_codes.found_location_at(lat, lng)
            store.append("<MISSING>")
            store.append(
                "https://www.thelittleclinic.com/scheduler/tlc/location/" + str(i["id"])
            )
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
