from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4
from sgrequests import SgRequests
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def get_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], granularity=Grain_4()
    )
    url = "https://biscuitville.com/"
    class_name = "location-address2"

    driver = get_driver(url, class_name)
    response = driver.page_source
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    }
    nonce = response.split('"nonce":')[1].split("}")[0].replace('"', "")

    base_url = "https://biscuitville.com/wp-admin/admin-ajax.php"
    s = SgRequests()
    for search_lat, search_lng in search:

        x = 0
        while True:
            x = x + 1
            if x == 10:
                raise Exception
            try:
                params = {
                    "action": "get_dl_locations",
                    "all": "false",
                    "radius": "100",
                    "lat": str(search_lat),
                    "lng": str(search_lng),
                    "current_location": "N",
                    "nonce": nonce,
                }
                data_stuff = s.post(base_url, data=params, headers=headers)
                data = data_stuff.json()
                break
            except Exception:
                driver = get_driver(url, class_name, driver=driver)
                response = driver.page_source
                nonce = response.split('"nonce":')[1].split("}")[0].replace('"', "")

        data_states = data["locations"].keys()
        for data_state in data_states:
            if data_state == "SOON":
                continue
            data_states_dict = data["locations"][data_state]
            data_cities = data_states_dict.keys()
            for data_city in data_cities:
                for location in data_states_dict[data_city]:
                    locator_domain = "biscuitville.com"
                    page_url = location["location_url"]
                    location_name = location["name"]
                    address = location["address"]
                    city = location["city"]
                    state = location["state"]
                    zipp = location["zip"]
                    country_code = "US"
                    store_number = location["id"]
                    phone = location["phone"]
                    location_type = location["service_type"]
                    latitude = location["lat"]
                    longitude = location["lng"]
                    hours = (
                        location["details"]
                        .replace(" \r\n", ", ")
                        .replace("\n", ", ")
                        .replace("\r", "")
                    )
                    hours = hours.split(", ,")[0]
                    search.found_location_at(latitude, longitude)

                    yield {
                        "locator_domain": locator_domain,
                        "page_url": page_url,
                        "location_name": location_name,
                        "latitude": latitude,
                        "longitude": longitude,
                        "city": city,
                        "store_number": store_number,
                        "street_address": address,
                        "state": state,
                        "zip": zipp,
                        "phone": phone,
                        "location_type": location_type,
                        "hours": hours,
                        "country_code": country_code,
                    }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
