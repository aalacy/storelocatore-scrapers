from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
import re
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
    driver = get_driver("https://www.rockandbrews.com/locations", "order-button")
    html = driver.page_source
    soup = bs(html, "html.parser")

    grids = soup.find_all("div", attrs={"class": "col-md-4 col-xs-12 pm-location"})

    for grid in grids:
        locator_domain = "rockandbrews.com"
        phone = "<MISSING>"

        name = grid.find("h4").text
        address = grid.find("span").text

        full_address = grid.find("a").text
        city_state_zipp = full_address.replace(address, "").strip()

        city = city_state_zipp.split(", ")[0]
        try:
            state = city_state_zipp.split(", ")[1].split(" ")[0]
            zipp = city_state_zipp.split(", ")[1].split(" ")[1]
        except Exception:
            if "Mexico" in city_state_zipp:
                city_parts = city.split(" ")[:-1]
                city = ""
                for part in city_parts:
                    city = city + " " + part

                city = city.strip()
                state = "<MISSING>"
                zipp = city_state_zipp.split("Mexico")[0].split(" ")[-1]

        if len(state) < 2:
            pass
        else:
            if state == "<MISSING>":
                country_code = "MX"

            else:
                country_code = "US"

            store_number = "<MISSING>"

            location_type = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            hour = (
                (
                    grid.find("div", attrs={"class": "hours"})
                    .text.split(" Happy")[0]
                    .split(" Kitchen")[0]
                )
                .replace("Â ", " ")
                .replace("Open early for Playoff Baseball!", "")
            )

            hour = "".join(c for c in hour if ord(c) < 128)

            page_url = (
                "https://www.rockandbrews.com"
                + grid.find("a", attrs={"class": "details-button"})["href"]
            )
            driver.get(page_url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "pm-custom-section-heading")
                )
            )

            html = driver.page_source
            soup = bs(html, "html.parser")

            div = soup.find("div", attrs={"id": "location"})
            try:
                phone = div.find("a")["href"].replace("tel:", "")
            except Exception:
                a_tags = soup.find_all("a")
                for tag in a_tags:
                    if "tel:" in tag["href"]:
                        phone = tag["href"].replace("tel:", "")

            if bool(re.search("[a-zA-Z]", phone)):
                phone = "<MISSING>"

            yield {
                "locator_domain": locator_domain,
                "page_url": page_url,
                "location_name": name,
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "store_number": store_number,
                "street_address": address,
                "state": state,
                "zip": zipp,
                "phone": phone,
                "location_type": location_type,
                "hours": hour,
                "country_code": country_code,
            }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(mapping=["street_address"]),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"]),
        zipcode=sp.MultiMappingField(mapping=["zip"]),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"]),
        store_number=sp.MappingField(
            mapping=["store_number"],
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(mapping=["location_type"]),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()

# https://www.rockandbrews.com/yaamava'-resort--and--casino
