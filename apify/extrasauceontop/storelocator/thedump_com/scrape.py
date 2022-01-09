from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
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
    driver = get_driver("https://thedump.com/locations", "thedump-location-title")

    soup = bs(driver.page_source, "html.parser")
    grids = soup.find_all("div", attrs={"class": "col-md-4 thedump-location-block"})

    for grid in grids:
        locator_domain = "thedump.com"
        page_url = locator_domain + grid.find("h3").find("a")["href"]
        location_name = grid.find("h3").text.strip()

        address_part = bs(
            str(grid.find("div", attrs={"class": "thedump-location-address"})).replace(
                "<br/>", " "
            ),
            "html.parser",
        ).text.strip()

        if "Newport News" in address_part:
            address_pieces = address_part.split(",")[0].split(" ")
            address = ""
            for x in range(len(address_pieces) - 2):
                address = address + address_pieces[x] + " "

            city = address_pieces[-2] + " " + address_pieces[-1]
        else:
            address_pieces = address_part.split(",")[0].split(" ")
            address = ""
            for x in range(len(address_pieces) - 1):
                address = address + address_pieces[x] + " "

            city = address_pieces[-1]

        state = location_name.split(", ")[1]
        zipp = address_part.split(", ")[1].split(" ")[-1]
        country_code = "US"
        store_number = "<MISSING>"

        try:
            phone = (
                grid.find("div", attrs={"class": "thedump-location-phone"})
                .find("a")["href"]
                .replace("tel:", "")
            )
        except Exception:
            phone = "<MISSING>"

        if "warehouse" in location_name.lower():
            location_type = "Warehouse"
        else:
            location_type = "Store"

        driver.get("https://" + page_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dump_store_home_container"))
        )

        lat_lon_soup = bs(driver.page_source, "html.parser")

        iframes = lat_lon_soup.find_all("iframe")

        for iframe in iframes:
            try:
                if "https://www.google.com/maps/embed?pb" in iframe["src"]:
                    lat_lon_url = iframe["src"]
                    break

            except Exception:
                continue

        latitude = lat_lon_url.split("!3d")[1].split("!")[0]
        longitude = lat_lon_url.split("!2d")[1].split("!3d")[0]

        try:
            hours = (
                grid.text.strip()
                .split(phone[-4:])[1]
                .split("View on Map")[0]
                .replace("  ", " ")
                .replace("  ", " ")
                .strip()
            )
        except Exception:
            hours = (
                grid.text.strip()
                .split("Pickups Only")[1]
                .split("View on Map")[0]
                .replace("  ", " ")
                .replace("  ", " ")
                .strip()
            )
        hours = hours.split("More")[0]
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
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(mapping=["city"], part_of_record_identity=True),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"]),
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
