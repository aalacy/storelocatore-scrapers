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

log = sglog.SgLogSetup().get_logger("kroger.com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://www.kroger.com/storelocator-sitemap.xml"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)
    soup = BeautifulSoup(driver.page_source, "lxml")

    for i, url in enumerate(soup.find_all("loc")[:-1]):
        page_url = url.text
        for i in range(6):
            log.info(page_url)
            driver.get(page_url)
            time.sleep(2)
            WebDriverWait(driver, 50).until(
                ec.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            time.sleep(2)
            location_soup = BeautifulSoup(driver.page_source, "lxml")

            location_name = ""
            try:
                script = location_soup.find(
                    "script", attrs={"type": "application/ld+json"}
                ).contents[0]
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
            if len(raw_address) != 1:
                street_address = raw_address[0].strip()
                city = raw_address[1].strip()
                state = raw_address[2].strip()
                zipp = raw_address[3].split("Get")[0].strip()
            else:
                raw_address = list(
                    location_soup.find(
                        class_="StoreAddress-storeAddressGuts"
                    ).stripped_strings
                )[0].split(",")
                street_address = " ".join(raw_address[0].split()[:-1])
                city = raw_address[0].split()[-1]
                state = raw_address[1].split()[0]
                zipp = raw_address[1].split()[1]
        country_code = "US"
        store_number = page_url.split("/")[-1]
        try:
            phone = data["telephone"]
        except:
            try:
                phone = location_soup.find(class_="PhoneNumber-phone").text.strip()
            except:
                phone = ""
        lat = data["geo"]["latitude"]
        lng = data["geo"]["longitude"]
        hours = " ".join(data["openingHours"])

        sgw.write_row(
            SgRecord(
                locator_domain="https://www.kroger.com/",
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
