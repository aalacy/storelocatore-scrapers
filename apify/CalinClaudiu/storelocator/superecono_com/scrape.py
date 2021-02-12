from sgscrape import simple_scraper_pipeline as sp
from sgscrape import sgpostal as parser
from sglogging import sglog


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

from sgselenium import SgFirefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.superecono.com/tiendas"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    pages = []
    links = soup.find_all(
        "a",
        {
            "class": lambda x: x
            and all(i in x for i in ["mpc-button", "mpc-transition", "mpc-inited"])
        },
    )
    for i in links:
        pages.append(i["href"])
    with SgFirefox() as driver:
        driver.get(url)
        soup = b4(driver.page_source, "lxml")
        pages = []
        links = soup.find_all(
            "a",
            {
                "class": lambda x: x
                and all(i in x for i in ["mpc-button", "mpc-transition", "mpc-inited"])
            },
        )
        for i in links:
            pages.append(i["href"])

        for i in pages:
            driver.get(i)

            test = driver.page_source
            soup = b4(test, "lxml")
            holdon = WebDriverWait(driver, 30).until(  # noqa
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="mapa"]/div[1]/div/div/div/div/div/iframe')
                )
            )
            driver.switch_to.frame(holdon)
            test = driver.page_source
            attempts = 0
            while 'class="address"' not in test and attempts < 30:
                attempts += 1
                time.sleep(1)
                test = driver.page_source

            soup1 = b4(test, "lxml")
            k = {}
            k["page_url"] = i

            try:
                k["location_name"] = soup.find(
                    "div", {"class": "wbp_wrapper"}
                ).text.strip()
            except Exception:
                k["location_name"] = "<MISSING>"

            try:
                raw_addr = soup1.find(
                    "div", {"class": "address", "jstcache": True}
                ).text
            except Exception:
                raw_addr = "<MISSING>"
            parsed = parser.parse_address_intl(raw_addr)
            k["street_address"] = parsed.street_address_1
            if parsed.street_address_2:
                k["street_address"] = (
                    k["street_address"] + ", " + parsed.street_address_2
                )
            k["city"] = parsed.city
            k["zipcode"] = parsed.postcode
            try:
                k["state"] = parsed.country.replace("Puerto Rico", "PR")
            except Exception:
                k["state"] = "<MISSING>"

            try:
                info = soup.find("ul", {"class": "info-tiendas"})
            except Exception:
                info = None

            try:
                k["phone"] = info.find("li", {"class": "tel"}).text.strip()
            except Exception:
                k["phone"] = "<MISSING>"

            if not k["street_address"]:
                try:
                    addressno = info.find("li", {"class": "dir"}).text.strip()
                    k["street_address"] = addressno
                except Exception:
                    pass

            try:
                k["hours"] = info.find_all("li", {"class": "hora"})
                h = []
                for j in k["hours"]:
                    h.append(j.text.strip())
                k["hours"] = "; ".join(h)
            except Exception:
                k["hours"] = "<MISSING>"

            k["raw"] = addressno + ", " + raw_addr
            yield k

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.superecono.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MissingField(),
        longitude=sp.MissingField(),
        street_address=sp.MappingField(
            mapping=["street_address"], part_of_record_identity=True
        ),
        city=sp.MappingField(mapping=["city"], part_of_record_identity=True),
        state=sp.MappingField(mapping=["state"], part_of_record_identity=True),
        zipcode=sp.MappingField(mapping=["zipcode"], part_of_record_identity=True),
        country_code=sp.MissingField(),
        phone=sp.MappingField(mapping=["phone"]),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MissingField(),
        raw_address=sp.MappingField(mapping=["raw"]),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
