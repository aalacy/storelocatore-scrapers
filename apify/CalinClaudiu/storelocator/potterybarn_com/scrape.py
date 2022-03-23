from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
from sgzip.dynamic import DynamicGeoSearch

from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def test_possible(driver, session):
    try:
        driver.get('https://www.potterybarn.com/')
        try:
            popup = WebDriverWait(driver, 10).until(  # noqa
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/div[9]/div/a",
                    )
                )
            )  # noqa
            popup.click()
        except Exception:
            pass
        findbutton = WebDriverWait(driver, 10).until(  # noqa
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[3]/header/div[1]/div/ul[2]/li[5]/nav/a",
                )
            )
        )  # noqa
        findbutton.click()
        time.sleep(15)
        #searchbar.send_keys("Berlin", Keys.RETURN)
        time.sleep(5)
        reqs = list(driver.requests)
        logzilla.info(f"Length of driver.requests: {len(reqs)}")
        for r in reqs:
            x = r.url
            logzilla.info(x)
            if "mcd-latam" in x and "near?country" in x:
                return (True, (x, r.headers, country["page"]))
        return (False, (None, None))
    except Exception:
        try:
            driver.get(country["page"])
            locator = WebDriverWait(driver, 10).until(  # noqa
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/div[1]/div/div/div/nav/div[2]/div[2]/div/a[1]",
                    )
                )
            )  # noqa
            locator.click()
            searchbar = WebDriverWait(driver, 10).until(  # noqa
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/div[1]/div/div/div/div[1]/div/div[1]/div[1]/div/div[1]/form/div/div[1]/div[1]/input",
                    )
                )
            )  # noqa
            time.sleep(3)
            searchbar.send_keys("Berlin", Keys.RETURN)
            time.sleep(10)
            reqs = list(driver.requests)
            logzilla.info(f"Length of driver.requests: {len(reqs)}")
            for r in reqs:
                x = r.url
                if "mcd-latam" in x and "near?country" in x:
                    logzilla.info(f" Found API for current country: {x}\n")
                    return (True, (x, r.headers, country["page"]))
            return (False, (None, None))
        except Exception as e:
            logzilla.info(str(e))
            return (False, (None, None))


def fetch_for_real(data, session):
    # data https://mcd-latam-landings-backend-l.gigigoapps.com/restaurants/near?country=BR&lat=52.52000659999999&lng=13.404954&radius=50000&limit=50
    def fix_data(data):
        copy = ""
        country = data.split("country=")[1].split("&", 1)[0]
        copy = data.split("lat=")[0] + "lat={}&lng={}&radius=50000&limit=50000"
        return country, copy

    def fetch_point(url, headers, session):
        headers = {}
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
        locations = None
        try:
            locations = SgRequests.raise_on_err(
                session.get(url, headers=headers)
            ).json()
        except Exception as e:
            logzilla.error(f"{e}")
        if locations:
            for rec in locations:
                yield rec

    country, url = fix_data(data[0])
    search = DynamicGeoSearch(
        country_codes=[country.lower()],
        expected_search_radius_miles=15,
    )
    for coord in search:
        for item in fetch_point(url.format(*coord), data[1], session):
            item["host"] = data[2]
            yield item


def fetch_data():
    with SgRequests() as session:
        if True:
            if True:
                with SgChrome(is_headless = False) as driver:
                    data = test_possible(driver, session)
                    logzilla.info(
                        f'{result}\n{data}\n{country["text"]} - {country["page"]}\n'
                    )
                    if result:
                        for rec in fetch_for_real(data, session):
                            yield rec

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(
            mapping=["host"],
        ),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["name"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["address"],
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["neighborhood"], is_required=False),
        zipcode=sp.MappingField(mapping=["cep"], is_required=False),
        country_code=sp.MappingField(mapping=["country"], is_required=False),
        phone=sp.MissingField(),
        store_number=sp.MappingField(
            mapping=["_id"],
            is_required=False,
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MappingField(mapping=["active"], is_required=False),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=10,
        duplicate_streak_failure_factor=-1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
