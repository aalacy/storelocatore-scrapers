import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("centura_org")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
    }
    adressessess = []
    base_url = "https://www.centura.org"
    page = 1
    while True:
        json_data = session.get(
            "https://www.centura.org/rest/solr/location-search?_format=json&search=&location=USA&radius=0&page="
            + str(page)
            + "&type=",
            headers=headers,
        ).json()["response"]["docs"]

        if json_data == []:
            break
        for data in json_data:
            try:
                location_name = data["ts_search_facility_name"]
            except:
                break
            try:
                street_address = (
                    data["ss_practice_address_line1"]
                    + " "
                    + str(data["ss_practice_address_line2"])
                )
            except:
                street_address = (
                    data["ss_facility_address_line1"]
                    + " "
                    + str(data["ss_facility_address_line2"])
                )
            try:
                city = data["ss_practice_city"]
            except:
                city = data["ss_facility_city"]
            try:
                state = data["ss_practice_state"]
            except:
                state = data["ss_facility_state"]
            try:
                zipp = data["ss_practice_postal_code"]
            except:
                zipp = data["ss_facility_postal_code"]
            country_code = "US"
            store_number = data["its_nid"]
            try:
                try:
                    phone = data["ss_field_practice_phone"]
                except:
                    phone = data["ss_field_facility_phone"]
            except:
                phone = "<MISSING>"
            try:
                location_type = data["sm_facility_type"][0]
            except:
                location_type = "<MISSING>"
            try:
                latitude = data["locs_field_practice_solr_lat_lng"].split(",")[0]
                longitude = data["locs_field_practice_solr_lat_lng"].split(",")[1]
            except:
                latitude = data["locs_field_facility_solr_lat_lng"].split(",")[0]
                longitude = data["locs_field_facility_solr_lat_lng"].split(",")[1]

            if data["ss_path"]:
                page_url = base_url + data["ss_path"]
            else:
                page_url = "<MISSING>"
            try:
                try:
                    hours = data["field_facility_hours"]
                except:
                    hours = data["field_practice_hours"]
            except:
                hours = "<MISSING>"

            if "Suite" in street_address:
                street_address = street_address.split("Suite")[0].strip()
            if "Ste" in street_address:
                street_address = street_address.split("Ste")[0].strip()
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address.replace("Floor", ""))
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            if str(store[2] + str(store[7]) + store[-1]) in adressessess:
                continue
            adressessess.append(str(store[2] + str(store[7]) + store[-1]))
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store
        page += 1


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
