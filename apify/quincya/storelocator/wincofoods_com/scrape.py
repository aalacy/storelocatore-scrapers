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

from sgrequests import SgRequests

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
    time.sleep(10)
    WebDriverWait(driver, 50).until(
        ec.presence_of_element_located((By.CLASS_NAME, "store-list__scroll-container"))
    )
    time.sleep(10)

    base = BeautifulSoup(driver.page_source, "lxml")

    items = base.find(class_="store-list__scroll-container").find_all("li")
    locator_domain = "https://www.wincofoods.com/"

    session = SgRequests()

    headers = {
        "authority": "www.wincofoods.com",
        "method": "GET",
        "scheme": "https",
        "cookie": "__cf_bm=d3pvbp9Zz1Sqbjf9ZpF73Ajf1JToUZo4_Yyj.hHbygI-1646798653-0-AZX8eb6f0PHqXxZEImyMKJdNxyLQ+68ll4lFoAPpJ6OpoXTQiIocfDApQZu/Uou3qG7Bb/EBeHZ3O30/KZdqmRX6wU2rAl6rgfCVAQM5ZxrrxU4GoEXpts2zCDd677u47qg5BG2aRO7WcuqeRryR4PHTDUQQiwK1mzzzIglClIoD; session=1646798653672.aiqd50jh; Srn-Auth-Token=3fab0fb6ec7f7938a0ae1374976659924556dfe092843ad3cad4e8eb9206fddd; _ga=GA1.2.1947025224.1646798656; _gid=GA1.2.1491679485.1646798656; _gat_UA-107931429-1=1; _gat_UA-18308088-1=1; XSRF-TOKEN=06dc963f164af05f82ae72ec4aee9f068c727cfb143377b36c434d356733ec78",
        "x-csrf-token": "06dc963f164af05f82ae72ec4aee9f068c727cfb143377b36c434d356733ec78",
        "x-newrelic-id": "XQYBWFVVGwEEUVlUBgcG",
        "sec-fetch-user": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

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
        api_link = (
            "https://www.wincofoods.com/proxy/store/getbyid?location_id=" + store_number
        )
        logger.info(link)

        store = session.get(api_link, headers=headers).json()["store"]
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        if "24" not in hours_of_operation:
            raw_hours = store["store_hours"]
            hours_of_operation = ""
            for row in raw_hours:
                num = row["day"]
                if num == 0:
                    day = "Sun"
                elif num == 1:
                    day = "Mon"
                elif num == 2:
                    day = "Tue"
                elif num == 3:
                    day = "Wed"
                elif num == 4:
                    day = "Thu"
                elif num == 5:
                    day = "Fri"
                elif num == 6:
                    day = "Sat"
                start = row["open"]
                close = row["close"]
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + start + "-" + close
                ).strip()

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
