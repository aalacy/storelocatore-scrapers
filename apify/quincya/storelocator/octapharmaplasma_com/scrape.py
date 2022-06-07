from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("octapharmaplasma.com")


def fetch_data(sgw: SgWriter):
    base_link = "https://www.octapharmaplasma.com/plasma-donation-centers/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.octapharmaplasma.com"

    states = base.find(class_="search_by_state").find_all("option")[1:]
    for i in states:
        state_link = i["value"]

        logger.info(state_link)
        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        items = base.find_all(class_="marker")
        for item in items:
            location_name = item.h5.text.strip()
            if "COMING SOON" in location_name.upper():
                continue
            raw_address = item.h6.text.split(",")
            street_address = ",".join(raw_address[:-2]).replace("  ", " ")
            city = raw_address[-2].strip()
            state = raw_address[-1].split()[0]
            zip_code = raw_address[-1].split()[1]
            country_code = "US"
            phone = item.find(class_="contact").text.strip()
            location_type = ""
            store_number = location_name.split("-")[-1].split()[-1]
            latitude = item["data-lat"]
            longitude = item["data-lng"]

            final_link = item.find(class_="btn button1").a["href"]
            req = session.get(final_link, headers=headers)
            page = BeautifulSoup(req.text, "lxml")
            hours_of_operation = " ".join(
                list(page.find(class_="timing").ul.stripped_strings)
            )

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
