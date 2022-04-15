from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
from selenium import webdriver
import undetected_chromedriver as uc
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    x = 0
    while True:
        x = x + 1
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("start-maximized")
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = uc.Chrome(
                executable_path=ChromeDriverManager().install(), options=options
            )

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
    url = "https://www.circalighting.com/showrooms/"
    class_name = "more"
    driver = get_driver(url, class_name)
    response = driver.page_source

    soup = bs(response, "html.parser")
    grids = soup.find_all("div", attrs={"class": "pagebuilder-column"})

    for grid in grids:
        if "coming soon" in grid.text.strip().lower():
            continue

        if "more information" not in grid.text.strip().lower():
            continue
        locator_domain = "circalighting.com"
        location_name = grid.find("h2").text.strip()
        page_url = grid.find("a", attrs={"tabindex": "0"})["href"]

        driver.get(page_url)
        location_response = driver.page_source

        latitude = (
            location_response.replace(" ", "")
            .split("LatLng")[1]
            .split("lat:")[1]
            .split(",")[0]
        )
        longitude = (
            location_response.replace(" ", "")
            .split("LatLng")[1]
            .split("lng:")[1]
            .split("}")[0]
        )

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        country_code = "US"

        p_tags = grid.find_all("p")

        if "now open" in p_tags[0].text.strip().lower():
            p_tags = p_tags[1:]

        address = p_tags[0].text.strip()

        try:
            city = p_tags[1].text.strip().split(", ")[0]
            state = location_name.split("-")[0].strip()
            zipp = p_tags[1].text.strip().split(", ")[1].split(" ")[1]

        except Exception:
            city = p_tags[1].text.strip().split(" ")[0]
            state = location_name.split("-")[0].strip()
            if state == "UK":
                state = "<MISSING>"
                country_code = "UK"

            zipp = "".join(part + " " for part in p_tags[1].text.strip().split(" ")[1:])

        index = 0
        for p_tag in p_tags:
            if "phone" in p_tag.text.strip().lower():
                phone = ""
                for character in p_tag.text.strip():
                    if character.isdigit() is True:
                        phone = phone + character
                break
            index = index + 1

        hours_parts = p_tags[index + 1 : -1]
        hours = ""
        for part in hours_parts:
            hours = hours + part.text.strip() + " "
        hours = hours[:-1]

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
