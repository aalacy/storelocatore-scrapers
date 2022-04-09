from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("af247_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://locations.af247.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    main_items = base.find_all(class_="Directory-listLink")

    final_links = []
    for main_item in main_items:
        link = base_link + main_item["href"]
        if main_item["href"].count("/") > 0:
            final_links.append(link)
        else:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            next_items = base.find_all(class_="Directory-listLink")
            for next_item in next_items:
                link = base_link + next_item["href"]
                final_links.append(link)

    for i, final_link in enumerate(final_links):
        final_req = session.get(final_link, headers=headers)
        logger.info(final_link)
        base = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "af247.com"

        location_name = base.find(id="location-name").text.strip()
        street_address = base.find(itemprop="streetAddress")["content"]
        city = base.find(class_="Address-field Address-city").text.strip()
        try:
            state = base.find(itemprop="addressRegion").text.strip()
        except:
            state = ""
        try:
            zip_code = base.find(itemprop="postalCode").text.strip()
        except:
            zip_code = ""
        country_code = base.find(itemprop="addressCountry").text.strip()

        try:
            phone = base.find(id="telephone").text.strip()
            if not phone:
                phone = ""
        except:
            phone = ""
        store_number = ""
        location_type = ""

        try:
            hours_of_operation = (
                " ".join(list(base.find(class_="c-hours-details").stripped_strings))
                .replace("Day of the Week Hours", "")
                .strip()
            )
        except:
            hours_of_operation = ""

        latitude = base.find(itemprop="latitude")["content"]
        longitude = base.find(itemprop="longitude")["content"]

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
