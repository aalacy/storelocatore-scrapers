import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    r = session.get("https://www.maryspizzashack.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for location in soup.find_all("div", {"class": "locations-item"}):
        location_request = session.get(location.find("a")["href"], headers=headers)
        location_soup = BeautifulSoup(location_request.text, "lxml")
        name = location.find("a")["href"].split("/")[-2]
        phone = location_soup.find("span", {"class": "phone"}).text
        hours = (
            " ".join(
                list(
                    location_soup.find(
                        "aside", {"id": "sidebar_location"}
                    ).stripped_strings
                )
            )
        ).split("Happy Hour")[0]
        address = list(
            location_soup.find(
                "div", {"class": "address-information col_5"}
            ).stripped_strings
        )
        lat = ""
        lng = ""
        for script in location_soup.find_all("script"):
            if "center: { lat: " in script.text:
                lat = script.text.split("center: { lat: ")[1].split(",")[0]
                lng = (
                    script.text.split("center: { lat: ")[1]
                    .split("lng:")[1]
                    .split("}")[0]
                )
        store = []
        store.append("https://www.maryspizzashack.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[1].split(" ")[-2])
        store.append(address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("mary's pizza shack")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(
            hours.replace("Store Hours ", "").strip() if hours != "" else "<MISSING>"
        )
        store.append(
            location.find("a")["href"] if location.find("a")["href"] else "<MISSING>"
        )
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
