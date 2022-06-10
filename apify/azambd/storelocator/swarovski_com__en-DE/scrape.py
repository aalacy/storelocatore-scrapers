from typing import Iterable, Tuple, Callable

from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.pause_resume import CrawlStateSingleton
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
import time
import json


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        lati, lngi = coord

        url = f"https://www.swarovski.com/en-AA/store-finder/list/?allBaseStores=true&geoPoint.latitude={lati}&geoPoint.longitude={lngi}&radius=1000"
        try:
            with SgRequests() as session:
                r = session.get(url, headers=headers)
                website = "swarovski.com"
                js = json.loads(r.content)["results"]
                logger.info(
                    f"[{current_country}] [{lati}, {lngi}] Stores: {len(js)}, Remaining Lat/Lng to Crawl: {items_remaining}"
                )

                for item in json.loads(r.content)["results"]:
                    name = item["displayName"]
                    store = item["name"]
                    loc = "https://www.swarovski.com" + item["url"]
                    lat = item["geoPoint"]["latitude"]
                    lng = item["geoPoint"]["longitude"]
                    found_location_at(lat, lng)
                    add = ""
                    if item["address"]["line1"] is not None:
                        add = item["address"]["line1"]
                    if item["address"]["line2"] is not None:
                        add = add + " " + item["address"]["line2"]
                    add = add.strip()
                    city = item["address"]["town"]
                    state = "<MISSING>"
                    zc = item["address"]["postalCode"]
                    if zc is None:
                        zc = "<MISSING>"
                    phone = item["address"]["phone"]
                    country = item["address"]["country"]["isocode"]

                    if country not in [
                        "AT",
                        "BE",
                        "CH",
                        "CZ",
                        "DE",
                        "ES",
                        "FR",
                        "GR",
                        "HK",
                        "HU",
                        "IE",
                        "IT",
                        "JP",
                        "KR",
                        "LU",
                        "MO",
                        "MY",
                        "NL",
                        "PL",
                        "PT",
                        "SG",
                        "TH",
                        "TR",
                        "TW",
                        "VE",
                    ]:
                        continue

                    typ = item["distributionType"]
                    hours = ""
                    for day in item["openingHours"]["weekDayOpeningList"]:
                        dname = day["weekDay"]
                        dopen = day["openingTime"]["formattedHour"]
                        dclose = day["closingTime"]["formattedHour"]
                        hrs = dname + ": " + dopen + "-" + dclose
                        if day["closed"]:
                            hrs = dname + ": Closed"
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
                    if len(phone) < 6:
                        phone = "<MISSING>"

                    yield SgRecord(
                        locator_domain=website,
                        page_url=loc,
                        location_name=name,
                        street_address=add,
                        city=city,
                        state=state,
                        zip_postal=zc,
                        country_code=country,
                        phone=phone,
                        location_type=typ,
                        store_number=store,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours,
                    )

        except Exception as e:
            logger.info(f"Failed for [{current_country}]: [{lati},{lngi}]: {e}")
            pass


if __name__ == "__main__":
    logger = sglog.SgLogSetup().get_logger(logger_name="swarovski.com")
    CrawlStateSingleton.get_instance().save(override=True)
    start = time.time()

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=50,
    )

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=[
                "AT",
                "BE",
                "CH",
                "CZ",
                "DE",
                "ES",
                "FR",
                "GR",
                "HK",
                "HU",
                "IE",
                "IT",
                "JP",
                "KR",
                "LU",
                "MO",
                "MY",
                "NL",
                "PL",
                "PT",
                "SG",
                "TH",
                "TR",
                "TW",
                "VE",
            ],
        )

        for rec in par_search.run():
            writer.write_row(rec)

    end = time.time()
    logger.info(f"Scrape took {(end-start)/60} minutes.")
