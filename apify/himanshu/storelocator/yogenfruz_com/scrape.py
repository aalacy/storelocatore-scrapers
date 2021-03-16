import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from geopy.geocoders import Nominatim


logger = SgLogSetup().get_logger("yogenfruz_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"
    }
    base_url = "https://www.yogenfruz.com"
    r = session.get("https://yogenfruz.com/find-a-store/", headers=headers)
    soup = BeautifulSoup(r.text, "html5lib")
    addresses = []

    location_name = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "yogen fruz"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    locs = soup.find_all("div", {"class": "location-search-result col-md-4"})
    for loc in locs:
        page_url = loc.find("a", {"class": "location-link"})["href"]
        if loc.find("div", {"class": "location-detail-address-3"}):
            city_state_zip = (
                loc.find("div", {"class": "location-detail-address-3"})
                .text.strip()
                .split(",")
            )
            zipp = city_state_zip[-1].strip()
        if len(zipp) == 5:
            country_code = "US"
        else:
            country_code = "CA"
        if loc.find("a", {"class": "address-block-phone"}):
            phone = loc.find("a", {"class": "address-block-phone"}).text.strip()
        for data in page_url:
            data = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(data.text, "html5lib")
            store_data = soup1.find("div", {"class": "vc_col-sm-4 location-details"})
            location_name = store_data.find("h3", {"class": "location-name"}).text
            street_address = store_data.find("div", {"class": "location_address"}).text
            city_state = store_data.find(
                "div", {"class": "location_address-2"}
            ).text.split(",")
            city = city_state[0]
            state = city_state[1]
            temp_hours_of_operation = list(
                soup1.find("div", {"class", "vc_col-sm-3 store-hours"}).stripped_strings
            )

            geolocator = Nominatim(user_agent="myGeocoder")
            try:
                location = geolocator.geocode(
                    street_address + "," + city + "," + state + "," + zipp
                )
                latitude = location.latitude
                longitude = location.longitude
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

        try:
            if len(temp_hours_of_operation) == 7:
                hours_of_operation = (
                    " ".join(temp_hours_of_operation)
                    .replace("Store Hours:", "")
                    .strip()
                )
            elif len(temp_hours_of_operation) == 5:
                hours_of_operation = (
                    " ".join(temp_hours_of_operation)
                    .replace("Store Hours:", "")
                    .strip()
                )
            else:
                hours_of_operation = (
                    " ".join(temp_hours_of_operation)
                    .replace("Store Hours:", "")
                    .strip()
                )
        except:
            hours_of_operation = "<MISSING>"

        if hours_of_operation == "Hours vary. Contact store location for more details.":
            hours_of_operation = "<MISSING>"

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
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url)
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
