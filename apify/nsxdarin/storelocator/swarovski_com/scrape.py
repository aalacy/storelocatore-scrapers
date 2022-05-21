from typing import Iterable, Tuple, Callable

from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.pause_resume import CrawlStateSingleton
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration

import json


session = SgRequests()


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
        url = f"https://www.swarovski.com/en-AA/store-finder/list/?allBaseStores=true&geoPoint.latitude={lati}&geoPoint.longitude={lngi}&radius=50&currentPage=1"

        try:
            r = session.get(url, headers=headers)
            website = "swarovski.com"
            res_json = json.loads(r.content)["results"]

            logger.info(f"[{current_country}] [{lati}, {lngi}] Stores: {len(res_json)}")
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
                phone = item["address"]["phone"]
                country = item["address"]["country"]["isocode"]
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
                if len(zc) < 2:
                    zc = "<MISSING>"
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
            logger.info(f"Failed for {lati} - {lngi}: {e}")
            pass


if __name__ == "__main__":
    logger = sglog.SgLogSetup().get_logger(logger_name="swarovski.com")
    CrawlStateSingleton.get_instance().save(override=True)
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=10,
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
                "US",
                "AE",
                "AL",
                "AM",
                "AT",
                "AU",
                "AW",
                "AZ",
                "BA",
                "BE",
                "BG",
                "BH",
                "BO",
                "BR",
                "CA",
                "CH",
                "CI",
                "CN",
                "CO",
                "CR",
                "CY",
                "CZ",
                "DE",
                "DK",
                "DO",
                "DZ",
                "EC",
                "EE",
                "EG",
                "ES",
                "FI",
                "FJ",
                "FR",
                "GB",
                "GE",
                "GI",
                "GN",
                "GR",
                "GT",
                "HK",
                "HR",
                "HU",
                "ID",
                "IE",
                "IL",
                "IN",
                "IQ",
                "IR",
                "IS",
                "IT",
                "JO",
                "JP",
                "KE",
                "KN",
                "KR",
                "KW",
                "KY",
                "KZ",
                "LB",
                "LC",
                "LK",
                "LT",
                "LU",
                "LV",
                "MA",
                "MD",
                "ME",
                "MG",
                "MK",
                "MN",
                "MO",
                "MT",
                "MU",
                "MY",
                "NC",
                "NL",
                "NO",
                "NZ",
                "OM",
                "PA",
                "PH",
                "PK",
                "PL",
                "PR",
                "PT",
                "PY",
                "QA",
                "RO",
                "RU",
                "SA",
                "SG",
                "SI",
                "SK",
                "SM",
                "SR",
                "SX",
                "TH",
                "TR",
                "TW",
                "UA",
                "AD",
                "UY",
                "UZ",
                "VA",
                "VE",
                "VN",
                "VU",
                "XK",
                "ZA",
            ],
        )

        for rec in par_search.run():
            writer.write_row(rec)
