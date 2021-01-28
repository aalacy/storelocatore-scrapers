import csv
from sgselenium import SgChrome
from sgzip.static import static_coordinate_list, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger("gamestop_com")

base_url = "https://www.gamestop.com/"


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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
        for rows in data:
            writer.writerows(rows)


def extract_csrf_token(driver):
    driver.refresh()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    csrf_input = soup.find("input", class_="csrf-protection")
    return csrf_input["value"]


MISSING = "<MISSING>"


def get(store, key):
    return store.get(key, MISSING) or MISSING


def fetch_stores(driver, data):
    return driver.execute_async_script(
        f"""
        var done = arguments[arguments.length - 1];
        var formData = new FormData()
        formData.append('radius', "{data["radius"]}")
        formData.append('lat', "{data["lat"]}")
        formData.append('long', "{data["long"]}")
        formData.append('csrf_token', "{data["csrf_token"]}")

        fetch('https://www.gamestop.com/on/demandware.store/Sites-gamestop-us-Site/default/Stores-FindStores?radius={data["radius"]}&lat={data["lat"]}&long={data["long"]}', {{
            method: 'POST',
            body: formData
        }})
            .then(res => res.json())
            .then(data => done(data))
    """
    )


def fetch_locations(coord, csrf_token, driver, tracker):
    lat, lng = coord

    data = fetch_stores(
        driver, {"radius": 100, "lat": lat, "long": lng, "csrf_token": csrf_token}
    )
    stores = []
    if "stores" in data:
        for store in data["stores"]:
            store_number = store["ID"]
            if store_number in tracker:
                continue
            tracker.append(store_number)

            location_name = get(store, "name")
            location_type = MISSING

            street_address = get(store, "address1")
            if street_address:
                street_address = street_address.replace(" None", "")

            if get(store, "address2") != MISSING:
                street_address += f', {get(store, "address2")}'

            city = get(store, "city")
            state = get(store, "stateCode")
            postal = get(store, "postalCode")
            country_code = get(store, "countryCode")
            latitude = get(store, "latitude")
            longitude = get(store, "longitude")

            phone = get(store, "phone")
            hours_of_operation = get(store, "storeHours")

            try:
                page_url = (
                    f"https://www.gamestop.com/store/us/{state}/{city}/{store_number}"
                )
            except:
                page_url = "<MISSING>"

            store = []
            store.append("gamestop.com")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(postal)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)

            stores.append(store)

    return stores


def get_driver():
    headers = {
        "accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "referer": "https://www.gamestop.com/stores/?showMap=true&horizontalView=true&isForm=true",
    }

    driver = SgChrome(user_agent=headers["User-Agent"]).driver()
    driver.set_script_timeout(300)
    return driver


def fetch_data():
    tracker = []

    search = static_coordinate_list(100, SearchableCountries.USA)
    search.extend(static_coordinate_list(100, SearchableCountries.CANADA))

    driver = get_driver()
    driver.get(
        "https://www.gamestop.com/stores/?showMap=true&horizontalView=true&isForm=true"
    )
    csrf_token = extract_csrf_token(driver)

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_locations, coord, csrf_token, driver, tracker)
            for coord in search
        ]

        for future in as_completed(futures):
            yield future.result()


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
