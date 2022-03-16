from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = SgLogSetup().get_logger("cemexusa.com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    api_link = "https://www.cemexusa.com/find-your-location?p_p_id=CEMEX_MAP_SEARCH&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=findTheNearestLocations&p_p_cacheability=cacheLevelPage&_CEMEX_MAP_SEARCH_locationName=USA"
    stores = session.get(api_link, headers=headers).json()["theNearestLocations"]

    locator_domain = "cemexusa.com"

    for store in stores:
        location_name = store["locationName"]
        street_address = store["locationAddress"]["locationStreet"]
        city = store["locationAddress"]["locationCity"]
        state = store["locationAddress"]["locationRegion"]
        zip_code = store["locationAddress"]["locationPostcode"]
        country_code = "US"
        store_number = ""
        latitude = store["locationAddress"]["locationCoordinates"]["latitude"]
        longitude = store["locationAddress"]["locationCoordinates"]["longitude"]
        hours_of_operation = store["openingHours"]
        location_type = ", ".join(store["productList"])
        phone = store["locationContact"]["locationOrdersPhone"]
        link = "https://www.cemexusa.com/-/" + store["url"]
        log.info(link)
        if not state or not phone:
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                phone = base.find(class_="ld-contactbox-contacts").a.text
            except:
                pass
            try:
                state = (
                    base.find(class_="ld-topbox-address-address")
                    .text.split(",")[-2]
                    .strip()
                )
            except:
                pass

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
