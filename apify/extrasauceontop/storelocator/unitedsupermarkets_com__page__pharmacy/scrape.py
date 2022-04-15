from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
import json
from sgscrape import simple_scraper_pipeline as sp


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects


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
    url = "https://www.unitedsupermarkets.com/rs/store-locator"
    driver = get_driver(url, "store-logo")
    response = driver.page_source

    json_objects = extract_json(response.split("stores =")[1])

    for location in json_objects:
        pharm_found = 0
        for service_type in location["ServiceStores"]:
            if service_type["ServiceName"] == "In-Store Pharmacy":
                pharm_found = 1
                break
        if pharm_found == 0:
            continue

        locator_domain = "https://www.unitedsupermarkets.com/"
        
        try:
            page_url = "https://www.unitedsupermarkets.com/rs/store-locator/" + location["AddressSEO"] + "/" + str(location["StoreID"])
        except Exception:
            continue

        location_name = location["StoreName"]
        if "united supermarkets" not in location_name.lower():
            continue

        latitude = location["Latitude"]
        longitude = location["Longitude"]
        city = location["City"]
        store_number = location["StoreID"]

        try:
            address = location["Address1"] + " " + location["Address2"]
        
        except Exception:
            address = location["Address1"]
        
        address = address.strip()
        state = location["State"]
        zipp = location["Zipcode"]
        location_type = "<MISSING>"
        country_code = "US"

        driver.get(page_url)
        location_response = driver.page_source

        location_json = extract_json(location_response.split("storeDetail =")[1])[0]

        phone = "<MISSING>"
        hours = "<MISSING>"
        
        for department in location_json["DepartmentStores"]:
            if "pharmacy" not in department["DepartmentName"].lower():
                continue

            phone = department["DepartmentPhone"]
            try:
                hours = "Monday-Friday: " + department["DepartmentMFHours"] + " Saturday: " + str(department["DepartmentSatHours"]) + " Sunday: " + str(department["DepartmentSunHours"])
            except Exception:
                pass

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