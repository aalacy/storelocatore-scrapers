import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


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

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://www.speedway.com/"
    soup = BeautifulSoup(
        session.post("https://www.speedway.com/Locations/Search", headers=headers).text,
        "lxml",
    )

    locations = soup.find_all("section", {"class": "c-location-card"})

    for data in locations:
        try:
            phone = data.find("li", {"data-location-details": "phone"}).text.strip()
        except:
            phone = "<MISSING>"
        street_address = data.find("a", {"class": "btn-get-directions"})[
            "data-location-address"
        ].split(",")[0]
        city = data.find("li", {"data-location-details": "address"}).text.split(",")[0]
        state = (
            data.find("li", {"data-location-details": "address"})
            .text.split(",")[1]
            .split(" ")[1]
        )
        zipp = (
            data.find("li", {"data-location-details": "address"})
            .text.split(",")[1]
            .split(" ")[2]
        )
        store_number = data["data-costcenter"]
        latitude = data["data-latitude"]
        longitude = data["data-longitude"]
        page_url = "https://www.speedway.com/locations/store/" + str(store_number)

        options = data.find_all("ul", {"class": "c-location-options__list"})
        hours = options[1] if len(options) > 1 else options[0]
        if "Open 24 Hours" in hours.find("li").text.strip().lstrip():
            hours_of_operation = hours.find("li").text.strip().lstrip()
        else:
            hours_of_operation = "<MISSING>"

        store = []
        store.append(base_url)
        store.append("<MISSING>")
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
