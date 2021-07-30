from typing import Iterable

from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch

from sglogging import sglog

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    headers = {}
    headers[
        "accept"
    ] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    headers["accept-encoding"] = "gzip, deflate, br"
    headers["accept-language"] = "en-US,en;q=0.9"
    headers["cache-control"] = "no-cache"
    headers["pragma"] = "no-cache"
    headers["sec-ch-ua-mobile"] = "?0"
    headers["sec-fetch-dest"] = "document"
    headers["sec-fetch-mode"] = "navigate"
    headers["sec-fetch-site"] = "none"
    headers["sec-fetch-user"] = "?1"
    headers["upgrade-insecure-requests"] = "1"
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
        url = str(
            f"https://www.choicehotels.com/webapi/location/hotels?adults=1&checkInDate=3021-07-15&checkOutDate=3021-07-17&favorCoOpHotels=false&hotelSortOrder=&include=&lat={lat}&lon={lng}&minors=0&optimizeResponse=&placeName=&platformType=DESKTOP&preferredLocaleCode=en-us&ratePlanCode=RACK&ratePlans=RACK%2CPREPD%2CPROMO%2CFENCD&rateType=LOW_ALL&rooms=1&searchRadius=100&siteName=us&siteOpRelevanceSortMethod=ALGORITHM_B"
        )
        try:
            locations = http.get(url, headers=headers).json()
        except Exception as e:
            logzilla.error(f"{e}")
            locations = {"hotelCount": 0}
        if locations["hotelCount"] > 0:
            for record in locations["hotels"]:
                try:
                    record["address"]["subdivision"] = record["address"]["subdivision"]
                except KeyError:
                    record["address"]["subdivision"] = SgRecord.MISSING
                try:
                    record["name"] = record["name"]
                except KeyError:
                    record["name"] = SgRecord.MISSING

                try:
                    record["phone"] = record["phone"]
                except KeyError:
                    record["phone"] = SgRecord.MISSING

                try:
                    record["brandCode"] = record["brandCode"]
                except KeyError:
                    record["brandCode"] = SgRecord.MISSING

                try:
                    record["brandName"] = record["brandName"]
                except KeyError:
                    record["brandName"] = SgRecord.MISSING

                try:
                    record["lon"] = record["lon"]
                except KeyError:
                    record["lon"] = SgRecord.MISSING

                try:
                    record["lat"] = record["lat"]
                except KeyError:
                    record["lat"] = SgRecord.MISSING

                try:
                    record["address"]["line1"] = record["address"]["line1"]
                except KeyError:
                    record["address"]["line1"] = SgRecord.MISSING
                try:
                    record["address"]["city"] = record["address"]["city"]
                except KeyError:
                    record["address"]["city"] = SgRecord.MISSING
                try:
                    record["address"]["postalCode"] = record["address"]["postalCode"]
                except KeyError:
                    record["address"]["postalCode"] = SgRecord.MISSING
                try:
                    record["address"]["country"] = record["address"]["country"]
                except KeyError:
                    record["address"]["country"] = SgRecord.MISSING

                try:
                    yield SgRecord(
                        page_url="https://www.choicehotels.com/" + str(record["id"]),
                        location_name=str(record["name"]),
                        street_address=str(record["address"]["line1"]),
                        city=str(record["address"]["city"]),
                        state=str(record["address"]["subdivision"]),
                        zip_postal=str(record["address"]["postalCode"]),
                        country_code=str(record["address"]["country"]),
                        store_number=str(record["id"]),
                        phone=str(record["phone"]),
                        location_type=str(
                            str(record["brandCode"]) + " - " + str(record["brandName"])
                        ),
                        latitude=str(record["lat"]),
                        longitude=str(record["lon"]),
                        locator_domain="https://www.choicehotels.com/",
                        hours_of_operation=SgRecord.MISSING,
                        raw_address=SgRecord.MISSING,
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
                        raw_address=str(record),
                    )
                    found += 1
                progress = (
                    str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
                )
                total += found
                logzilla.info(
                    f"{str(lat).replace('(','').replace(')','')}{str(lon).replace('(','').replace(')','')}|found: {found}|total: {total}|prog: {progress}|\nRemaining: {search.items_remaining()} Searchable: {SearchableCountry}"
                )


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL, expected_search_radius_miles=100
    )
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
