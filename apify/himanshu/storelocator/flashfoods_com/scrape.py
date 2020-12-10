import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://www.flashfoods.com/"
    for page in range(1, 11):
        r = session.get(
            "https://www.flashfoods.com/store-locator/page/" + str(page) + "/",
            headers=headers,
        )
        soup = BeautifulSoup(r.text, "lxml")
        for row in soup.find_all("div", {"class": "store-row"}):
            store_number = row.find("div", {"data-th": "Store#"}).text.strip()
            street_address = row.find("div", {"data-th": "Address"}).text.strip()
            city = row.find("div", {"data-th": "City"}).text.strip()
            state = row.find("div", {"data-th": "State"}).text.strip()
            zipp = row.find("div", {"data-th": "Zip"}).text.strip()
            phone = row.find("div", {"data-th": "Phone#"}).text.strip()
            location_type = row.find("div", {"data-th": "Type"}).text.strip()
            location_name = "<MISSING>"
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            page_url = "<MISSING>"

            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append(store_number)
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            store = [x.strip() if type(x) == str else x for x in store]

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
