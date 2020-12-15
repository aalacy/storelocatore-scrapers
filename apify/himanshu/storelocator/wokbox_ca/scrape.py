from sgrequests import SgRequests
import csv
from bs4 import BeautifulSoup

session = SgRequests()


def fetch_data():
    url = "https://wokbox.ca/locations#map1"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    container = soup.find("table")
    rows = container.find_all("tr")
    del rows[0]
    for row in rows:
        locator_domain = "https://wokbox.ca/locations"
        name = row.find(class_="wpgmza_table_title all").get_text()
        address = row.find(class_="wpgmza_table_address").get_text().split()
        street = " ".join(address[0:-3]).replace("#", "").replace(",", "")
        city = address[-3]
        state = "<MISSING>"
        pin = address[-2] + " " + address[-1]
        country_code = "CA"
        store_number = "<MISSING>"
        desc = row.find(class_="wpgmza_table_description").get_text().split()
        for index, h in enumerate(desc):
            if "Phone" in h:
                hours = " ".join(desc[:index])
                phone = desc[index + 1]

        lat = "<MISSING>"
        lng = "<MISSING>"
        page_url = row.find(class_="wpgmza_table_description").find("a")

        store = []
        store.append(locator_domain if locator_domain else "<MISSING>")
        store.append(name if name else "<MISSING>")
        store.append(street if street else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state)
        store.append(pin if pin else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number)
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours if hours else "<MISSING>")
        store.append(page_url.get("href") if page_url else "<MISSING>")
        yield store


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


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
