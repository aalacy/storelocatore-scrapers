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
    addressess = []
    base_url = "https://www.tenthousandvillages.com/"
    states = [
        "CA",
        "CO",
        "CT",
        "FL",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "MD",
        "MA",
        "MI",
        "MN",
        "NE",
        "NH",
        "NY",
        "NC",
        "OH",
        "PA",
        "TN",
        "TX",
        "VT",
        "VA",
        "WA",
    ]
    for state in states:
        payload = (
            '{"zip":"","state":"'
            + state
            + '","context":"checkout","form_key":"ceNWiN7LvNokGvU4"}'
        )
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "Content-Type": "text/plain",
        }
        json_data = session.post(
            "https://www.tenthousandvillages.com/stores/search/index",
            data=payload,
            headers=headers,
        ).json()
        for val in json_data:
            location_name = val["name"]
            if val["address_2"] is not None:
                address2 = val["address_2"]
            else:
                address2 = ""

            if val["address_1"] is not None:
                address1 = val["address_1"]
            else:
                address1 = ""

            street_address = address1 + " " + address2
            city = val["city"]
            state = val["state"]
            zipp = val["zip"]
            country_code = val["country"]
            store_number = val["store_id"]
            phone = val["phone"]
            location_type = val["type"]
            latitude = val["latitude"]
            longitude = val["longitude"]
            page_url = "https://www.tenthousandvillages.com/" + val["url"]
            r1 = session.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            hours_of_operation = ", ".join(
                list(soup1.find("section", {"class": "sphours"}).stripped_strings)[1:]
            )

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
