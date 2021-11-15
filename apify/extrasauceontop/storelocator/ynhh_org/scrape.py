from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import time
import ssl
from sglogging import sglog
from tenacity import retry  # noqa
from tenacity import stop_after_attempt  # noqa

ssl._create_default_https_context = ssl._create_unverified_context
log = sglog.SgLogSetup().get_logger(logger_name="ynhh")


@retry(stop=stop_after_attempt(10))
def driver_retry(user_agent, url, class_name):
    try:
        driver = SgChrome(
            executable_path=ChromeDriverManager().install(),
            user_agent=user_agent,
            is_headless=True,
        ).driver()
        driver.get(url)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
        return driver

    except Exception:
        driver.quit()
        raise Exception("10 consecutive attempts blocked. Retry with a proxy")


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    driver = driver_retry(user_agent, url, class_name)

    return driver


def get_data():
    done_q = "No"
    page_number = 0
    while True:
        start_url = "https://www.ynhh.org/find-a-location.aspx?page=1&keyword=&sortBy=&distance=0&cz=&locs=0&within=Yale+New+Haven+Hospital&avail=0#sort=relevancy&numberOfResults=25&f:deliverynetwork=[Yale%20New%20Haven%20Hospital]"
        driver = get_driver(start_url, "map-location")
        log.info("got driver")
        for num in range(page_number):
            num = num
            try:
                driver.find_element_by_class_name("coveo-pager-next").click()
            except Exception:
                done_q = "Yes"
                break

            time.sleep(5)

        if done_q == "Yes":
            break
        html = driver.page_source
        soup = bs(html, "html.parser")

        grids = soup.find_all("div", attrs={"class": "card-content"})
        page_number = page_number + 1
        for grid in grids:
            location_name = grid.find(
                "a", attrs={"class": "CoveoResultLink"}
            ).text.strip()
            log.info(location_name)
            locator_domain = "ynhh.org"
            page_url = (
                "https://www.ynhh.org"
                + grid.find("a", attrs={"class": "CoveoResultLink"})["href"]
            )
            address_parts = str(grid.find("p")).split("<br/>")

            address = ""
            for part in address_parts[:-1]:
                address = address + part + " "

            address = address[:-1].replace("<p>", "")
            city = address_parts[-1].split(", ")[0].strip()
            state = address_parts[-1].split(", ")[-1].split(" ")[0]
            zipp = address_parts[-1].split(", ")[-1].split(" ")[-1].replace("</p>", "")

            country_code = "US"
            store_number = "<MISSING>"

            try:
                phone = (
                    grid.find_all("p")[-1]
                    .text.strip()
                    .split("Main")[-1]
                    .split("\n")[0]
                    .strip()
                )
            except Exception:
                phone = "<MISSING>"

            location_type = "<MISSING>"
            count = 0
            while True:
                try:
                    driver.get(page_url)
                    WebDriverWait(driver, 60).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "location-geo"))
                    )
                    break
                except Exception:
                    count = count + 1
                    if count == 10:
                        raise Exception
            location_soup = bs(driver.page_source, "html.parser")
            latitude = location_soup.find(
                "input", attrs={"class": "location-geo", "type": "hidden"}
            )["value"].split(",")[0]
            longitude = (
                location_soup.find(
                    "input", attrs={"class": "location-geo", "type": "hidden"}
                )["value"]
                .split(",")[1]
                .strip()
            )

            try:
                hours_parts = [
                    part
                    for part in location_soup.find("div", attrs={"class": "card"})
                    .text.strip()
                    .split("\n")
                    if part != "" and part.lower() != "hours"
                ]

            except Exception:
                hours = "<MISSING>"

            try:
                if hours_parts[0] != "M":
                    hours = "<MISSING>"

                else:
                    hours = ""
                    for part in hours_parts:

                        if "vary" in part:
                            hours = "<MISSING>"
                            break

                        if "(" in part:
                            break

                        if ": " in part:
                            break

                        hours = hours + part + " "

            except Exception:
                hours = "<MISSING>"

            hours = hours.strip()
            if zipp in state:
                state = zipp
                zipp = "<MISSING>"

            if "Fax" in phone:
                phone = location_soup.find(
                    "a", attrs={"class": "phone-number"}
                ).text.strip()

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
                "phone": phone.replace("203-867-5254", "").strip(),
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
