import re
import ssl
import time

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("wincofoods.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.wincofoods.com/stores/"
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    driver = SgChrome(user_agent=user_agent).driver()
    driver.get(base_link)
    WebDriverWait(driver, 30).until(
        ec.presence_of_element_located((By.CLASS_NAME, "store-list__scroll-container"))
    )
    time.sleep(10)

    base = BeautifulSoup(driver.page_source, "lxml")

    items = base.find(class_="store-list__scroll-container").find_all("li")
    locator_domain = "https://www.wincofoods.com/"

    for item in items:
        location_name = " ".join(list(item.find(class_="name").stripped_strings)[:2])
        street_address = list(item.find(class_="address1").stripped_strings)[-1]
        city = list(item.find(class_="city").stripped_strings)[-1]
        state = list(item.find(class_="state").stripped_strings)[-1]
        zip_code = list(item.find(class_="zip").stripped_strings)[-1]
        country_code = "US"
        location_type = ""
        store_number = item["id"].split("-")[-1]
        hours_of_operation = list(
            item.find(class_="store-preview__status").stripped_strings
        )[-1].title()

        link = "https://www.wincofoods.com/stores/" + store_number
        logger.info(link)
        got_page = False

        try:
            driver.get(link)
            WebDriverWait(driver, 30).until(
                ec.presence_of_element_located((By.CLASS_NAME, "address1"))
            )
            time.sleep(5)
            got_page = True
        except:
            logger.info("Retrying link ..")
            try:
                driver.get(link)
                WebDriverWait(driver, 30).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "address1"))
                )
                time.sleep(5)
                got_page = True
            except:
                pass

        if got_page:
            base = BeautifulSoup(driver.page_source, "lxml")
            phone = base.find("a", {"href": re.compile(r"tel:")}).text
            latitude = base.find("meta", attrs={"property": "og:location:latitude"})[
                "content"
            ]
            longitude = base.find("meta", attrs={"property": "og:location:longitude"})[
                "content"
            ]
            hours_of_operation = " ".join(
                list(
                    base.find(class_="store-details-store-hours__list").stripped_strings
                )
            )
        else:
            phone = "<INACCESSIBLE>"
            latitude = "<INACCESSIBLE>"
            longitude = "<INACCESSIBLE>"
            hours_of_operation = "<INACCESSIBLE>"

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
    driver.close()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
