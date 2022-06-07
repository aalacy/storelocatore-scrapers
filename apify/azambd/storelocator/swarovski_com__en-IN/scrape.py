from typing import Iterable, Tuple, Callable
from sgpostal.sgpostal import parse_address_intl
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

MISSING = "<MISSING>"


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            return street_address, city, state

    except Exception:
        pass
    return MISSING, MISSING, MISSING


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:
        """
        This crawl is only for IN
        This method gets called on each iteration of the search.
        It provides you with all the data you could get from the search instance, as well as
        a method to register found locations.

        :param coord: The current coordinate (lat, long)
        :param zipcode: The current zipcode (In DynamicGeoSearch instances, please ignore!)
        :param current_country: The current country (don't assume continuity between calls - it's meant to be parallelized)
        :param items_remaining: Items remaining in the search - per country, if `ParallelDynamicSearch` is used.
        :param found_location_at: The equivalent of `search.found_location_at(lat, long)`
        """

        lati, lngi = coord

        url = f"https://www.swarovski.com/en-AA/store-finder/list/?allBaseStores=true&geoPoint.latitude={lati}&geoPoint.longitude={lngi}&radius=5000"

        session = SgRequests()
        r = session.get(url, headers=headers)
        website = "swarovski.com"
        res_json = json.loads(r.content)["results"]

        logger.info(
            f"[{current_country}] [{lati}, {lngi}] Stores: {len(res_json)}, {items_remaining}"
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
            city1 = item["address"]["town"]
            raw_address = f"{add}, {city1}"
            street_address, city, state = get_address(raw_address)
            zc = item["address"]["postalCode"]
            if zc is None:
                zc = MISSING

            phone = item["address"]["phone"]
            country = item["address"]["country"]["isocode"]
            # Filter India
            if "IN" not in str(country):
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
                phone = MISSING

            raw_address = f"{add}, {city1} {zc}"
            raw_address = raw_address.replace(MISSING, "").replace(",,", ", ")

            yield SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=street_address,
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
                raw_address=raw_address,
            )


if __name__ == "__main__":
    logger = sglog.SgLogSetup().get_logger(logger_name="swarovski.com")
    CrawlStateSingleton.get_instance().save(override=True)
    start = time.time()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=300,
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
            country_codes=["IN"],
        )

        for rec in par_search.run():
            writer.write_row(rec)

    end = time.time()
    logger.info(f"Scrape took {(end-start)/60} minutes.")
