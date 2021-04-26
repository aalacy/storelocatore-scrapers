from sgscrape import simple_scraper_pipeline as sp
from sgscrape import sgpostal as parser
from sglogging import sglog


from bs4 import BeautifulSoup as b4

from sgselenium import SgFirefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


def try_again_addr(soup, soup1, raw_addr, k):
    addr_candidates = []
    goodSoFar = ""
    freshData = (
        soup.find("div", {"class": "wpb_wrapper"})
        .find("li", {"class": "dir"})
        .text.strip()
    )

    for i in list(k[j] for j in ["city", "state", "zipcode"]):
        if i:
            if i.strip() not in freshData:
                goodSoFar = goodSoFar + i + " "
    goodSoFar = goodSoFar.strip()
    addr_candidates.append(str(freshData + " " + goodSoFar))
    for i in addr_candidates:
        x = ""
        parsed = parser.parse_address_intl(i)
        if parsed.street_address_1:
            x = x + parsed.street_address_1
            if parsed.street_address_2:
                x = x + ", " + parsed.street_address_2
        if x:
            return x


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.superecono.com/tiendas"
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
            k["location_name"] = ""

            try:
                k["location_name"] = soup.find(
                    "div", {"class": "wbp_wrapper"}
                ).text.strip()
            except Exception:
                k["location_name"] = ""
            if not k["location_name"]:
                try:
                    k["location_name"] = soup1.find(
                        "div", {"class": "place-name"}
                    ).text.strip()
                except Exception:
                    k["location_name"] = "<MISSING>"

            try:
                raw_addr = soup1.find(
                    "div", {"class": "address", "jstcache": True}
                ).text
            except Exception:
                raw_addr = "<MISSING>"

            if all(
                string in raw_addr
                for string in ["852", "uebrada", "rujillo", "00976", "lto"]
            ):
                raw_addr = "Carr. 852 Km. 2.7 Bo. Quebrada Grande Trujillo Alto 00976 Puerto Rico"
            parsed = parser.parse_address_intl(raw_addr)
            k["street_address"] = (
                parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
            )
            if parsed.street_address_2:
                k["street_address"] = (
                    k["street_address"] + ", " + parsed.street_address_2
                )
            k["city"] = parsed.city if parsed.city else "<MISSING>"
            k["zipcode"] = parsed.postcode if parsed.postcode else "<MISSING>"
            k["state"] = ""
            if parsed.state:
                k["state"] = parsed.state
            else:
                if parsed.country:
                    k["state"] = parsed.country.replace("Puerto Rico", "PR")
            if not k["state"]:
                k["state"] = "<MISSING>"

            if all(
                string in raw_addr
                for string in ["Paseo del Caf", "Yauco", "00698", "Puerto Rico"]
            ):
                k["street_address"] = "Calle Comercio Paseo del Café #48"
                k["city"] = "Yauco"
                k["zipcode"] = "00698"
                k["state"] = "PR"
            try:
                info = soup.find("ul", {"class": "info-tiendas"})
            except Exception:
                info = None

            try:
                k["phone"] = info.find("li", {"class": "tel"}).text.strip()
            except Exception:
                k["phone"] = "<MISSING>"
            addressno = None
            try:
                addressno = info.find("li", {"class": "dir"}).text.strip()
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
            if addressno and k["street_address"]:
                if len(addressno) > len(k["street_address"]):
                    k["street_address"] = addressno
            k["raw"] = addressno + ", " + raw_addr if addressno else raw_addr

            try:
                k["latitude"], k["longitude"] = (
                    soup1.find("div", {"class": "google-maps-link"})
                    .find("a")["href"]
                    .split("ll=", 1)[1]
                    .split("&", 1)[0]
                    .split(",")
                )
            except Exception:
                k["latitude"], k["longitude"] = ["<MISSING>", "<MISSING>"]

            if k["latitude"] == "<MISSING>":
                try:
                    k["latitude"], k["longitude"] = (
                        soup1.find("a", {"jstcache": "46"})["href"]
                        .split("ll=", 1)[1]
                        .split("&", 1)[0]
                        .split(",")
                    )
                except Exception:
                    k["latitude"], k["longitude"] = ["<MISSING>", "<MISSING>"]
            if k["street_address"] == "<MISSING>":
                k["street_address"] = try_again_addr(soup, soup1, raw_addr, k)
            yield k

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.superecono.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
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
