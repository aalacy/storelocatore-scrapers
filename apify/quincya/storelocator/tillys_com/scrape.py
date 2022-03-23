import ssl
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
import os

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data(sgw: SgWriter):

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    base_link = "http://www.tillys.com/store-list/?"

    driver = SgChrome(
        executable_path=ChromeDriverManager().install(), user_agent=user_agent
    ).driver()
    time.sleep(2)
    driver.get(base_link)
    driver.find_element(By.CSS_SELECTOR, "body")
    time.sleep(40)

    base = BeautifulSoup(driver.page_source, "lxml")

    locator_domain = "tillys.com"

    stores = base.find_all(class_="col-6 col-sm-3 sl__stores-list_item")

    for i, store in enumerate(stores):
        location_name = store.find(class_="sl__stores-list_name-link").text.strip()

        if "coming soon" in location_name.lower():
            continue

        link = (
            "https://www.tillys.com"
            + store.find(class_="sl__stores-list_name-link")["href"]
        )

        raw_address = list(
            store.find("div", attrs={"itemprop": "address"}).stripped_strings
        )

        try:
            phone = store.find("div", attrs={"itemprop": "telephone"}).text.strip()
        except:
            phone = "<INACCESSIBLE>"

        if (len(raw_address) == 3 and phone != "<INACCESSIBLE>") or len(
            raw_address
        ) == 2:
            street_address = raw_address[0].strip()
            city = raw_address[1].split(",")[0].strip()
            state = raw_address[1].split(",")[1].strip().split("\n")[0]
            zip_code = raw_address[1].split(",")[1].strip().split("\n")[1]
        elif len(raw_address) == 4 or phone == "<INACCESSIBLE>":
            street_address = raw_address[0].strip() + " " + raw_address[1].strip()
            city = raw_address[2].split(",")[0].strip()
            state = raw_address[2].split(",")[1].strip().split("\n")[0]
            zip_code = raw_address[2].split(",")[1].strip().split("\n")[1]

        country_code = "US"
        store_number = link.split("=")[-1]
        if not store_number.isnumeric():
            store_number = "<MISSING>"
        location_type = "<MISSING>"

        if "temporarily closed" in str(store).lower():
            hours_of_operation = "Temporarily Closed"
        else:
            try:
                days = list(store.time.stripped_strings)[:7]
            except:
                continue
            hours = list(store.time.stripped_strings)[7:]
            hours_of_operation = ""
            for i in range(len(days)):
                hours_of_operation = (
                    hours_of_operation + " " + days[i] + " " + hours[i]
                ).strip()

        geo = (
            store.find("a", string="Driving directions")["href"]
            .split("//")[-1]
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state.replace("RH", "RI"),
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

    driver.close()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
