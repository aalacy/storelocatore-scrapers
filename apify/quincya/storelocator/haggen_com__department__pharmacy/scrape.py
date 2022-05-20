import ssl
import time

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium import SgChrome

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.haggen.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.haggen.com/find-our-stores/"

    driver = SgChrome(user_agent=user_agent).driver()

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="crunchyBox")

    for item in items:
        raw_address = list(item.stripped_strings)
        if "pharmacy" not in raw_address[4].lower():
            continue
        location_name = raw_address[0]
        street_address = raw_address[1]
        city = raw_address[2].split(",")[0].strip()
        state = raw_address[2].split(",")[1].strip().split()[0]
        zip_code = raw_address[2].split(",")[1].strip().split()[1]
        country_code = "US"
        store_number = item["id"].split("-")[1]
        location_type = ""
        phone = raw_address[4].split(":")[1].strip()

        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = " ".join(
            list(base.find("h3", string="Pharmacy:").find_next("p").stripped_strings)[
                1:
            ]
        ).replace("—", "-")

        driver.get(link)
        time.sleep(4)

        raw_gps = driver.find_element_by_xpath(
            "//*[(@title='Open this area in Google Maps (opens a new window)')]"
        ).get_attribute("href")
        latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find(",")].strip()
        longitude = raw_gps[raw_gps.find(",") + 1 : raw_gps.find("&")].strip()

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
