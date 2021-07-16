import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

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
    addresses = []
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    base_url = (
        "https://www.bathandbodyworks.com/north-america/global-locations-canada.html"
    )
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("div", {"class": "store-location"})
    for i in data:
        data2 = i.find("p", {"class": "location"})
        state = data2.text.split(",")[-1].strip()
        city = data2.text.split(",")[0].strip()
        location_name = i.find("p").text
        data3 = i.find("p", {"class": "title"})
        phone = data3.find_next_sibling().text
        store = []
        store.append("https://www.bathandbodyworks.com/")
        store.append(location_name if location_name else "<MISSING>")
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])
        store.append("<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append("<MISSING>")
        store.append("CA")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(base_url)
        yield store
    base_url = "https://www.bathandbodyworks.com"
    r = session.get(
        "https://www.bathandbodyworks.com/on/demandware.store/Sites-BathAndBodyWorks-Site/en_US/Stores-GetNearestStores?latitude=40.7895453&longitude=-74.05652980000002&countryCode=US&distanceUnit=mi&maxdistance=100000&BBW=1",
        headers=headers,
    )
    location_data = r.json()["stores"]
    addresses = []
    for key in location_data:
        store_data = location_data[key]
        store = []
        store.append("https://www.bathandbodyworks.com")
        store.append(store_data["name"])
        store.append(store_data["address1"] + " " + store_data["address2"])
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])
        store.append(store_data["city"])
        store.append(store_data["stateCode"])
        store.append(store_data["postalCode"])
        store.append(store_data["countryCode"])
        store.append(key)
        store.append(store_data["phone"])
        store.append("<MISSING>")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        store.append(
            " ".join(
                list(BeautifulSoup(store_data["storeHours"], "lxml").stripped_strings)
            )
        )
        store.append("https://www.bathandbodyworks.com/store-locator")

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
