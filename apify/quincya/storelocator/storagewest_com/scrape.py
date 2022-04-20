import re
import ssl

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgselenium.sgselenium import SgChrome

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("storagewest.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.storagewest.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="sow-image-container")
    locator_domain = "https://www.storagewest.com"

    driver = SgChrome(user_agent=user_agent).driver()

    all_links = []
    for item in items:
        link = locator_domain + item.a["href"]
        if "locations" not in link:
            continue

        logger.info(link)
        driver.get(link)
        WebDriverWait(driver, 30).until(
            ec.presence_of_element_located((By.ID, "wpsl-stores"))
        )
        base = BeautifulSoup(driver.page_source, "lxml")

        links = base.find(id="wpsl-stores").ul.find_all("li", recursive=False)
        for i in links:
            all_links.append([i.a["href"], i["data-store-id"]])
    driver.close()

    for i in all_links:
        final_link = i[0]
        logger.info(final_link)
        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = list(base.find(class_="mb-5").stripped_strings)
        location_name = raw_address[0]
        street_address = raw_address[1].replace(",", "").strip()
        city_line = raw_address[2].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        location_type = ""
        store_number = i[1]
        phone = base.find(class_="mb-5").find("a", {"href": re.compile(r"tel:")}).text
        hours_of_operation = (
            " ".join(list(base.find(class_="mb-5").table.stripped_strings))
            .split("Closed on")[0]
            .strip()
        )

        latitude = ""
        longitude = ""

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=final_link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
