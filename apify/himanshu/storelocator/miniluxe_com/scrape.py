import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    header = {
        "User-agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5"
    }
    return_main_object = []
    base_url = "https://miniluxe.com/"
    loacation_url = base_url + "locations/"
    r = session.get(loacation_url, headers=header)
    soup = BeautifulSoup(r.text, "lxml")

    d = soup.find_all("div", {"class": "location"})

    for target_list in d:

        locator_domain = base_url
        location_name = target_list.find("a", {"class": "location-title"}).text.strip()
        page_url = target_list.find("a", {"class": "location-title"})["href"]
        ck = list(
            target_list.find("div", {"class": "location_address"}).stripped_strings
        )

        street_address = ck[0].strip()

        city = ck[1].strip().split(",")[0].strip()
        state = ck[1].strip().split(",")[1].strip()

        zip = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "miniluxe"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = target_list.find("div", {"class": "location-email"}).text.strip()

        hours_of_operation = "; ".join(
            target_list.find("div", {"class": "location-hours"})
            .text.strip()
            .split("\n")
        ).strip()
        store = []
        store.append(locator_domain if locator_domain else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")

        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")

        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
