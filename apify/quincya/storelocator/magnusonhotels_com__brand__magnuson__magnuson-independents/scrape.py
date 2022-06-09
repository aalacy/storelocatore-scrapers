import time
import json
import ssl

from bs4 import BeautifulSoup
from random import randint

from sgrequests import SgRequests

from sgselenium.sgselenium import SgChrome

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger(
    "magnusonhotels_com__brand__magnuson__magnuson-independents"
)

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    driver = SgChrome().driver()
    time.sleep(2)

    base_link = "https://www.magnusonhotels.com/brand/magnuson-independents/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()

    final_links = []
    req = session.get(base_link, headers=HEADERS)
    time.sleep(randint(1, 2))
    try:
        main_base = BeautifulSoup(req.text, "lxml")
    except (BaseException):
        logger.info("[!] Error Occured. ")
        logger.info("[?] Check whether system is Online.")

    items = main_base.find_all(class_="hoteltop")

    for item in items:
        link = item.a["href"].split("/")[-1]
        if link not in final_links:
            final_links.append(link)

    try:
        last_page = int(main_base.find_all(class_="page-numbers")[-2].text)
        for page_num in range(2, last_page + 1):
            page_link = base_link + "page/" + str(page_num)
            req = session.get(page_link, headers=HEADERS)
            time.sleep(randint(1, 2))
            try:
                main_base = BeautifulSoup(req.text, "lxml")
            except (BaseException):
                logger.info("[!] Error Occured. ")
                logger.info("[?] Check whether system is Online.")

            items = main_base.find_all(class_="hoteltop")

            for item in items:
                link = item.a["href"].split("/")[-1]
                if link not in final_links:
                    final_links.append(link)
    except:
        pass

    for link in final_links:
        final_link = "https://api.magnusonhotels.com/api/v1/hotels/find/" + link
        logger.info(final_link)
        try:
            if (
                final_link
                == "https://api.magnusonhotels.com/api/v1/hotels/find/atria-hotel-and-rv-mcgregor"
            ):
                raise
            req = session.get(final_link, headers=HEADERS)
            base = BeautifulSoup(req.text, "lxml")
            store = json.loads(base.text)["result"]
            got_api = True
        except:
            got_api = False

        if got_api:
            location_name = store["name"]
            locator_domain = "magnusonhotels.com"
            raw_address = store["addresses"].split(",")
            street_address = raw_address[-1].strip()
            city = raw_address[0].strip()
            state = raw_address[1].strip()
            if not state:
                state = "<MISSING>"
            zip_code = store["zipcode"]
            if " " in zip_code:
                country_code = "CA"
            else:
                country_code = "US"
            store_number = store["id"]
            raw_types = store["amenities"]
            location_type = ""
            for raw_type in raw_types:
                location_type = location_type + "," + raw_type["name"]
            location_type = location_type[1:]
            phone = store["phone"]
            if (
                phone[:1] != "1"
                or "London" in state
                or "BA" in state
                or "Bahamas" in state
            ):
                continue
            hours_of_operation = "<MISSING>"
            latitude = store["lat"]
            longitude = store["lng"]
            if location_name == "Luxury Park Inn Hotel":
                latitude = "29.7345029"
                longitude = "-95.4249255"
        else:
            final_link = "https://www.magnusonhotels.com/hotel/" + link
            driver.get(final_link)
            time.sleep(randint(8, 10))
            base = BeautifulSoup(driver.page_source, "lxml")
            location_name = base.h1.text
            locator_domain = "magnusonhotels.com"
            raw_address = base.find(class_="hotellocation").text.split(",")
            street_address = raw_address[-1].strip()
            city = raw_address[0].strip()
            state = raw_address[1].strip()
            zip_code = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            location_type = (
                base.find(class_="row amenities-list display-flex")
                .text.replace("\xa0", "")
                .replace("\n\n\n", ",")
                .strip()
            )
            phone = (
                base.find(class_="singlehotelcontact")
                .text.replace("\xa0", "")
                .replace("Hotel reception", "")
                .strip()
            )
            hours_of_operation = "<MISSING>"
            if location_name == "Atria Hotel and RV McGregor":
                latitude = "31.4432593"
                longitude = "-97.4142666"
            elif location_name == "Western States Inn San Miguel":
                latitude = "35.7492155"
                longitude = "-120.6998082"
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

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

    driver.close()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
