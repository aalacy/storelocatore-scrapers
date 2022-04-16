import json
import ssl
import time

from bs4 import BeautifulSoup

from sglogging import sglog

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome

log = sglog.SgLogSetup().get_logger("bakersplus.com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):
    base_url = "https://www.bakersplus.com/"

    base_link = "https://www.bakersplus.com/storelocator-sitemap.xml"
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)
    soup = BeautifulSoup(driver.page_source, "lxml")

    for url in soup.find_all("loc")[:-1]:
        page_url = url.text

        log.info(page_url)
        for i in range(6):
            driver.get(page_url)
            WebDriverWait(driver, 50).until(
                ec.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            time.sleep(2)
            location_soup = BeautifulSoup(driver.page_source, "lxml")
            script = location_soup.find(
                "script", attrs={"type": "application/ld+json"}
            ).contents[0]

            location_name = ""
            try:
                data = json.loads(script)
                street_address = data["address"]

                location_name = location_soup.find(
                    "h1", {"data-qa": "storeDetailsHeader"}
                ).text.strip()

                if location_name:
                    break
            except:
                log.info("Retrying ..")

        try:
            street_address = data["address"]["streetAddress"]
            city = data["address"]["addressLocality"]
            state = data["address"]["addressRegion"]
            zipp = data["address"]["postalCode"]
        except:
            raw_address = (
                location_soup.find(class_="StoreAddress-storeAddressGuts")
                .get_text(" ")
                .replace(",", "")
                .replace(" .", ".")
                .replace("..", ".")
                .split("  ")
            )
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = raw_address[2].strip()
            zipp = raw_address[3].split("Get")[0].strip()
        country_code = "US"
        store_number = page_url.split("/")[-1]
        phone = data["telephone"]
        lat = data["geo"]["latitude"]
        lng = data["geo"]["longitude"]
        hours = " ".join(data["openingHours"])

        sgw.write_row(
            SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )
        )

    driver.close()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
