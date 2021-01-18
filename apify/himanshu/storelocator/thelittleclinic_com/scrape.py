import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()


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
    zip_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=100,
        max_radius_miles=200,
    )
    adressess = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    }
    for zip_code in zip_codes:
        r = session.get(
            "https://www.thelittleclinic.com/tlc/api/clinic/search?freeFormAddress="
            + str(zip_code)
            + "&maxResults=300&pageSize=500",
            headers=headers,
        )
        json_data = r.json()
        j = json_data["results"]
        for i in j:
            store = []
            store.append("https://www.thelittleclinic.com/")
            store.append(i["legalName"])
            store.append(i["address"]["addressLine1"])
            store.append(i["address"]["city"])
            store.append(i["address"]["stateCode"])
            store.append(i["address"]["zip"])
            store.append(i["address"]["countryCode"])
            store.append(i["storeNumber"])
            store.append(i["phoneNumber"])
            store.append(i["banner"])
            store.append(i["latitude"])
            store.append(i["longitude"])
            store.append("<INACCESSBLE>")
            store.append(
                "https://www.thelittleclinic.com/scheduler/tlc/location/"
                + str(i["clinicId"])
            )
            if store[2] in adressess:
                continue
            adressess.append(store[2])
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
