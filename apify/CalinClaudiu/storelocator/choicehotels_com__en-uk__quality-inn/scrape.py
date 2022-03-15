from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_8
from sgzip.dynamic import DynamicGeoSearch
from sglogging import sglog

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


class ExampleSearchIteration:
    def do(search, coord, http1):
        lat, lng = coord
        lat = round(lat, 5)
        lng = round(lng, 5)
        url = str(
            f"https://www.choicehotels.com/webapi/location/hotels?adults=1&checkInDate=3022-02-13&checkOutDate=3022-02-14&lat={lat}&lon={lng}&optimizeResponse=image_url&platformType=DESKTOP&preferredLocaleCode=en-us&ratePlans=RACK%2CPREPD%2CPROMO%2CFENCD&rateType=LOW_ALL&rooms=1&searchRadius=100"
        )
        headers = {}
        headers[
            "accept"
        ] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        headers["accept-encoding"] = "gzip, deflate, br"
        headers["accept-language"] = "en-US,en;q=0.9"
        headers["cache-control"] = "no-cache"
        headers["pragma"] = "no-cache"
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        try:
            locations = SgRequests.raise_on_err(http1.get(url, headers=headers)).json()
            errorName = None
        except Exception as e:
            locations = {"hotelCount": 0}
            locations["status"] = "FAIL"
            errorName = str(e)
            logzilla.error(f"{errorName}")
        if (
            locations["status"] == "OK"
            and locations["hotelCount"] > 0
            and "NONEXISTENT_HOTEL_INFO" not in str(locations)
        ):
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
                    search.found_location_at(record["lat"], record["lon"])
                except Exception:
                    pass

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
                        raw_address=errorName if errorName else SgRecord.MISSING,
                    )
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


def dattafetch(search, http1):
    for coord in search:
        for item in ExampleSearchIteration.do(search, coord, http1):
            yield item


if __name__ == "__main__":
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL,
        granularity=Grain_8(),
        expected_search_radius_miles=100,
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STORE_NUMBER,
                },
                fail_on_empty_id=True,
            )
        )
    ) as writer:
        with SgRequests() as http1:
            for rec in dattafetch(search, http1):
                writer.write_row(rec)
