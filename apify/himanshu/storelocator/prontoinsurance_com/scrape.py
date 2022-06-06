from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="prontoinsurance.com")

session = SgRequests()


def fetch_data(sgw: SgWriter):
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    locator_domain = "prontoinsurance.com"

    found_poi = []

    max_distance = 50

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
    )

    log.info("Running sgzip ..")
    for postcode in search:
        payload = {"Zip_code": postcode}
        base_link = "https://www.prontoinsurance.com:3010/cmspages/agentsearch"
        try:
            stores = session.post(
                base_link, headers=headers, data=payload, timeout=5
            ).json()["agents"]
        except:
            continue
        for store in stores:
            location_name = store["name"]
            link = "https://www.prontoinsurance.com/agentdetail/" + store["slug"]
            street_address = store["Address"].split("(In")[0].split(", CA")[0]
            city = store["City"].replace(",", "")
            state = store["State"]
            zip_code = store["Zip_code"]
            country_code = "US"
            store_number = store["id"]
            location_type = "<MISSING>"
            phone = store["phone"]
            latitude = store["Latitude"]
            longitude = store["Longitude"]
            search.found_location_at(float(latitude), float(longitude))
            if link in found_poi:
                continue
            log.info(link)
            found_poi.append(link)
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                hours_of_operation = (
                    base.find(class_="agent_bx_widget mt ng-star-inserted")
                    .ul.get_text(" ")
                    .strip()
                )
            except:
                hours_of_operation = ""

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
