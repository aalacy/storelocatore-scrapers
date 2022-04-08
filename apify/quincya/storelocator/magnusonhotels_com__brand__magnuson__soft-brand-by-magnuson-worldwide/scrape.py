import json
import ssl
import time

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgselenium.sgselenium import SgChrome

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("magnusonhotels.com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://www.magnusonhotels.com/our-brands/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.magnusonhotels.com"

    driver = SgChrome(user_agent=user_agent).driver()

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    main_base = BeautifulSoup(req.text, "lxml")

    base_links = main_base.find_all(class_="greyghostbtn btn")

    final_links = []

    for i in base_links:

        base_link = i["href"]
        logger.info(base_link)
        req = session.get(base_link, headers=headers)
        main_base = BeautifulSoup(req.text, "lxml")
        items = main_base.find_all(class_="hoteltop")

        for item in items:
            link = item.a["href"].split("/")[-1]
            if link not in final_links:
                final_links.append(link)

        try:
            last_page = int(main_base.find_all(class_="page-numbers")[-2].text)
            next_page = main_base.find_all(class_="page-numbers")[-2]["href"].split(
                "page/"
            )[0]
            for page_num in range(2, last_page + 1):
                page_link = locator_domain + next_page + "page/" + str(page_num)
                req = session.get(page_link, headers=headers)
                main_base = BeautifulSoup(req.text, "lxml")

                items = main_base.find_all(class_="hoteltop")
                for item in items:
                    link = item.a["href"].split("/")[-1]
                    if link not in final_links:
                        final_links.append(link)
        except:
            pass

    for link in final_links:
        page_url = "https://www.magnusonhotels.com/hotel/" + link
        logger.info(page_url)
        final_link = "https://api.magnusonhotels.com/api/v1/hotels/find/" + link
        try:
            req = session.get(final_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            store = json.loads(base.text)["result"]
            location_name = store["name"]
            raw_address = store["addresses"].split(",")
            street_address = raw_address[-1].strip()
            city = raw_address[0].strip()
            state = raw_address[1].strip()
            if not state:
                if "Ohio" in location_name:
                    state = "OH"
            zip_code = store["zipcode"]
            if "000000" in zip_code:
                zip_code = ""
            store_number = store["id"]
            location_type = store["hotelBrand"]["brandname"]
            phone = store["phone"]
            hours_of_operation = "<MISSING>"
            latitude = store["lat"]
            longitude = store["lng"]
        except:
            logger.info("API failed..Trying Sgselenium")

            driver.get(page_url)
            time.sleep(10)
            base = BeautifulSoup(driver.page_source, "lxml")
            location_name = base.h1.text
            raw_address = base.find(class_="hotellocation").text.split(",")
            street_address = raw_address[-1].strip()
            city = raw_address[0].strip()
            state = raw_address[1].strip()
            zip_code = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
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

        if phone[:1] == "1" and "ON" not in state:
            country_code = "US"
        elif "ON" in state:
            country_code = "CA"
        elif "RP" in state:
            country_code = "Germany"
        elif " " in zip_code:
            country_code = "GB"
        else:
            country_code = ""
        if "Bahamas" in state:
            country_code = "Bahamas"

        if str(latitude) == "0.0":
            latitude = ""
            longitude = ""

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
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
