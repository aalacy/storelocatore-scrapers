import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup


session = SgRequests()


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
    base_url = "https://www.thriftyfoods.com"

    hdr = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    r = session.get(
        "https://www.thriftyfoods.com/api/en/Store/get?Latitude=48.45423&Longitude=-123.359205&Skip=0&Max=60000000",
        headers=hdr,
    ).json()
    return_main_object = []
    for loc in r["Data"]:
        page_url = loc["StoreDetailPageUrl"]
        r1 = session.get(base_url + loc["StoreDetailPageUrl"])
        soup = BeautifulSoup(r1.text, "lxml")
        hour = ""
        hour = " ".join(
            soup.find("div", {"id": "body_0_main_0_PnlOpenHours"}).stripped_strings
        )
        name = loc["Name"].strip()
        address = loc["AddressMain"]["Line"].strip()
        zip = loc["AddressMain"]["DisplayPostalCode"].strip()
        city = loc["AddressMain"]["City"].strip()
        state = loc["AddressMain"]["Province"].strip()
        lat = loc["Coordinates"]["Latitude"]
        lng = loc["Coordinates"]["Longitude"]
        phone = loc["PhoneNumberHome"]["Number"]
        country = "CA"
        store = []
        store.append(base_url)
        store.append(page_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("thriftyfoods")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
