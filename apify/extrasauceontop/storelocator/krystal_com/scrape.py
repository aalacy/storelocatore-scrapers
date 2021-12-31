from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape import simple_scraper_pipeline as sp
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
    base_url = "https://www.krystal.com/locations/"
    class_name = "nuxt-link-active"
    driver = get_driver(base_url, class_name)
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=25
    )

    for search_code in search:

        search_url = f"https://www.krystal.com/api?address={search_code}"

        x = 0
        while True:
            x = x + 1
            try:
                data = driver.execute_async_script(
                    """
                    var done = arguments[0]
                    fetch('"""
                    + search_url
                    + """', {
                        headers: {
                            path: 'locations/search'
                        }
                    })
                    .then(res => res.json())
                    .then(data => done(data))
                    """
                )
                break
            except Exception:
                if x == 10:
                    raise Exception

                continue

        try:
            data["locations"]

        except Exception:
            raise Exception
        for location in data["locations"]:
            try:
                locator_domain = "krystal.com"
                try:
                    page_url = "https://www.krystal.com/locations/" + location["path"]
                except Exception:
                    page_url = "<MISSING>"
                location_name = location["address"]
                latitude = location["lat"]
                longitude = location["lng"]
                search.found_location_at(latitude, longitude)
                city = location["city"]
                store_number = location["id"]
                address = location["address"]
                state = location["state"]
                zipp = location["zip"]
                phone = location["phone"]
                location_type = location["name"]
                country_code = location["country"]

                hours = ""

                try:
                    for hours_part in location["hours"]:
                        day = hours_part["day"]
                        start = hours_part["open"]
                        end = hours_part["close"]

                        try:
                            hours = hours + day + " " + start + "-" + end + ", "
                        except Exception:
                            continue

                    hours = hours[:-2]

                except Exception:
                    raise Exception

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

            except Exception:
                raise Exception


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
