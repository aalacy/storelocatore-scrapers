import time

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("poolcorp_com")


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    main_link = "https://www.poolcorp.com/sales-centers/index.html?z="

    max_distance = 175

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=max_distance,
        expected_search_radius_miles=max_distance,
    )

    logger.info("Running sgzip ..")
    for postcode in search:
        base_link = "https://www.poolcorp.com/map_api/?z=%s" % (postcode)
        logger.info(base_link)

        try:
            stores = session.get(base_link, headers=headers).json()["locations"]
        except:
            logger.info("Timeout..Retrying ..")
            time.sleep(10)
            session = SgRequests()
            stores = session.get(base_link, headers=headers).json()["locations"]

        for store in stores:
            locator_domain = "poolcorp.com"

            location_name = "POOLCORP - " + store["sitename"].split(",")[0].strip()
            if "colombia" in location_name.lower():
                continue
            street_address = store["address1"]
            city = store["city"]
            state = store["state"]

            if "-" in state:
                state = store["sitename"].split(",")[1].strip()

            if state == "QLD" or state == "NSW":
                continue

            zip_code = store["zip"]
            store_number = store["sitenumber"]
            try:
                phone = store["phone"].replace("(", "").replace(")", "")
            except:
                phone = ""
            latitude = store["latlon"].split(",")[0]
            longitude = store["latlon"].split(",")[1]
            search.found_location_at(float(latitude), float(longitude))

            if " " in zip_code:
                country_code = "CA"
            else:
                country_code = "US"

            logo = store["company_logo"].split("/")[-1]
            if "scp" in logo:
                location_type = "SCP Distributors LLC"
            elif "spp" in logo:
                location_type = "Superior Pool Products"
            elif "horizon" in logo:
                location_type = "Horizon Distributors Inc"
            elif "npt" in logo:
                location_type = "NPT"
            elif "jetline" in logo:
                location_type = "Jet Line"
            else:
                location_type = logo

            hours_of_operation = "<MISSING>"
            link = main_link + postcode

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
