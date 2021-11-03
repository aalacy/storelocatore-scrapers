from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    with SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent=user_agent,
        is_headless=True,
    ).driver() as driver:
        driver.get("https://www.metro.ca/en/find-a-grocery")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "hero--small"))
        )
        soup = bs(driver.page_source, "html.parser")

    locations = soup.find_all("li", attrs={"class": "fs--box-shop"})

    for location in locations:
        locator_domain = "metro.ca"
        page_url = "https://www.metro.ca" + location.find("a")["href"]
        location_name = location["data-store-name"]
        address = (
            location.find("div", attrs={"class": "address--line1"})
            .find("span")
            .text.strip()
        )
        city = location.find("span", attrs={"class": "address--city"}).text.strip()
        state = location.find(
            "span", attrs={"class": "address--provinceCode"}
        ).text.strip()
        zipp = location.find(
            "span", attrs={"class": "address--postalCode"}
        ).text.strip()
        country_code = "CA"
        store_number = location["data-store-id"]
        phone = (
            location.find("div", attrs={"class": "store-phone"})
            .find("span")
            .text.strip()
            .split("/")[0]
        )
        location_type = "<MISSING>"
        latitude = location["data-store-lat"]
        longitude = location["data-store-lng"]

        hours = "<INACCESSIBLE>"

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

    driver.quit()


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
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
