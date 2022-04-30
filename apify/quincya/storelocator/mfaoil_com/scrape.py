import re
import ssl
import time

from random import randint

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import sglog

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium import SgChrome

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="mfaoil.com")

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.mfaoil.com"

    driver = SgChrome(user_agent=user_agent).driver()

    max_distance = 100

    dup_tracker = []

    search = DynamicZipSearch(
        country_codes=[
            SearchableCountries.USA,
        ],
        max_search_distance_miles=max_distance,
    )

    driver.get("https://www.mfaoil.com/store-locator/")
    WebDriverWait(driver, 50).until(
        ec.presence_of_element_located((By.ID, "searchBox"))
    )
    for postcode in search:
        log.info(postcode)
        search_element = driver.find_element_by_id("searchBox")
        search_element.clear()
        search_element.send_keys(postcode)
        time.sleep(randint(1, 2))

        search_button = driver.find_element_by_id("search-btn")
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(randint(3, 4))

        base = BeautifulSoup(driver.page_source, "lxml")

        stores = base.find_all(class_="result-details")
        for store in stores:
            location_name = store.h3.get_text(" ").strip()
            if "store/" not in store.find_all("a")[-1]["href"]:
                continue
            link = locator_domain + store.find_all("a")[-1]["href"]
            if link in dup_tracker:
                continue
            dup_tracker.append(link)
            map_str = store.find(string="Directions").find_previous("a")["href"]
            geo = re.findall(r"[0-9]{2}\.[0-9]+%2C-[0-9]{2,3}\.[0-9]+", map_str)[
                0
            ].split("%2C")
            latitude = float(geo[0])
            longitude = float(geo[1])
            search.found_location_at(latitude, longitude)

            raw_address = list(store.p.stripped_strings)
            street_address = raw_address[0].strip()
            city_line = raw_address[-1].strip().split()
            city = " ".join(city_line[:-2]).strip()
            state = city_line[-2].strip()
            zip_code = city_line[-1].strip()
            country_code = "US"
            phone = store.find(id="phone").text.strip()
            if not phone:
                phone = "<MISSING>"
            location_type = "<MISSING>"

            log.info(link)
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            store_number = base.body["class"][-1].split("-")[-1]
            hours_of_operation = ""
            try:
                hours_of_operation = base.find(class_="fueling").text.strip()
            except:
                pass
            try:
                raw_hours = (
                    " ".join(list(base.find(class_="hours").stripped_strings))
                    .split("Location")[0]
                    .strip()
                )
                hours_of_operation = (hours_of_operation + " " + raw_hours).strip()
            except:
                pass
            try:
                location_type = ", ".join(
                    list(base.find(class_="aminities").stripped_strings)
                ).strip()
            except:
                pass
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
