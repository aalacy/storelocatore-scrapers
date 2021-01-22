import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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

    base_url = "https://www.hollisterco.com"

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }

    requests = SgRequests()

    r = requests.get(
        "https://www.hollisterco.com/shop/ViewAllStoresDisplayView?storeId=11205&catalogId=10201&langId=-1",
        headers=headers,
    )
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("li", {"class": "view-all-stores__store"})
    for link in data:

        if (
            "/clothing-stores/CA/" in link.a["href"]
            or "/clothing-stores/US/" in link.a["href"]
            or "/clothing-stores/GB/" in link.a["href"]
        ):
            page_url = base_url + link.a["href"]
            r = requests.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")
            if (
                soup.find(
                    lambda tag: (tag.name == "script") and "geoNodeUniqueId" in tag.text
                )
                is None
            ):
                continue
            json_data = json.loads(
                soup.find(
                    lambda tag: (tag.name == "script") and "geoNodeUniqueId" in tag.text
                )
                .text.split("try {digitalData.set('physicalStore',")[1]
                .split(");}")[0]
            )
            location_name = json_data["name"]
            street_address = json_data["addressLine"][0]
            city = json_data["city"]
            state = json_data["stateOrProvinceName"]
            zipp = json_data["postalCode"]
            country_code = json_data["country"]
            store_number = json_data["storeNumber"]
            phone = json_data["telephone"]
            location_type = "<MISSING>"
            latitude = json_data["latitude"]
            longitude = json_data["longitude"]
            hours_of_operation = "<INACCESSIBLE>"

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
            yield store
        else:
            pass  # another country location


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
