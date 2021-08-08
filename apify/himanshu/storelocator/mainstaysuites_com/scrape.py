from typing import Iterable

from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch

from sglogging import sglog
import random

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    headers = {}
    headers["x-requested-with"] = "XMLHttpRequest"
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    state = CrawlStateSingleton.get_instance()
    maxZ = None
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        found = 0
        rec_count = state.get_misc_value(
            search.current_country(), default_factory=lambda: 0
        )
        state.set_misc_value(search.current_country(), rec_count + 1)
        url = str(f"https://www.starbucks.com/bff/locations?lat={lat}&lng={lng}")
        try:
            locations = http.get(url, headers=headers).json()
            errorName = None
        except Exception as e:
            logzilla.error(f"{e}")
            locations = {"paging": {"total": 0}}
            errorName = str(e)
        if locations["paging"]["total"] > 0:
            for record in locations["stores"]:
                try:
                    yield SgRecord(
                        page_url="https://www.starbucks.com/store-locator/store/{}/{}".format(
                            str(record["id"]), str(record["slug"])
                        ),
                        location_name=str(record["name"]),
                        street_address=fix_comma(
                            str(
                                str(record["address"]["streetAddressLine1"])
                                + ","
                                + str(record["address"]["streetAddressLine2"])
                                + ","
                                + str(record["address"]["streetAddressLine3"])
                            )
                        ),
                        city=str(record["address"]["city"]),
                        state=str(record["address"]["countrySubdivisionCode"]),
                        zip_postal=str(record["address"]["postalCode"]),
                        country_code=str(record["address"]["countryCode"]),
                        store_number=str(record["id"]),
                        phone=str(record["phoneNumber"]),
                        location_type=str(
                            str(record["brandName"])
                            + " - "
                            + str(record["ownershipTypeCode"])
                        ),
                        latitude=str(record["coordinates"]["latitude"]),
                        longitude=str(record["coordinates"]["longitude"]),
                        locator_domain="https://www.starbuck.com/",
                        hours_of_operation=str(record["schedule"]),
                        raw_address=errorName if errorName else SgRecord.MISSING,
                    )
                    found += 1
                except KeyError:
                    yield SgRecord(
                        page_url=SgRecord.MISSING,
                        location_name=SgRecord.MISSING,
                        street_address=SgRecord.MISSING,
                        city=SgRecord.MISSING,
                        state=SgRecord.MISSING,
                        zip_postal=SgRecord.MISSING,
                        country_code=SgRecord.MISSING,
                        store_number=str(record["id"]),
                        phone=SgRecord.MISSING,
                        location_type=SgRecord.MISSING,
                        latitude=SgRecord.MISSING,
                        longitude=SgRecord.MISSING,
                        locator_domain=SgRecord.MISSING,
                        hours_of_operation=SgRecord.MISSING,
                        raw_address=errorName if errorName else str(record),
                    )
                    found += 1
                progress = (
                    str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
                )
                total += found
                logzilla.info(
                    f"{str(lat).replace('(','').replace(')','')}{str(lng).replace('(','').replace(')','')}|found: {found}|total: {total}|prog: {progress}|\nRemaining: {search.items_remaining()}"
                )
        else:
            yield SgRecord(
                page_url=SgRecord.MISSING,
                location_name=SgRecord.MISSING,
                street_address=SgRecord.MISSING,
                city=SgRecord.MISSING,
                state=SgRecord.MISSING,
                zip_postal=SgRecord.MISSING,
                country_code=SgRecord.MISSING,
                store_number=random.random(),
                phone=SgRecord.MISSING,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                locator_domain=SgRecord.MISSING,
                hours_of_operation=SgRecord.MISSING,
                raw_address=errorName,
            )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL,
        expected_search_radius_miles=None,
        max_search_results=49,
    )
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
