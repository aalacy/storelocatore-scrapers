from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_4
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import sglog

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def format_hours(hours_json):
    DAYS = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    formatted = []
    day_index = (DAYS.index(hours_json[2]["dayName"].lower()) - 2) % 7
    for schedule in hours_json:
        day = DAYS[day_index].capitalize()
        day_index = (day_index + 1) % 7
        hours = schedule["hours"]
        formatted.append(f"{day}: {hours}")
    return ", ".join(formatted)


def clean(x):
    if not x or x.lower() in ["none", "na"]:
        return SgRecord.MISSING
    else:
        return x


def fix_comma(x):
    x = x.replace("None", "")
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def ret_record(record):
    page_url = SgRecord.MISSING
    location_name = SgRecord.MISSING

    street_address = SgRecord.MISSING

    city = SgRecord.MISSING

    state = SgRecord.MISSING

    zip_postal = SgRecord.MISSING

    country_code = SgRecord.MISSING

    store_number = SgRecord.MISSING

    phone = SgRecord.MISSING

    location_type = SgRecord.MISSING

    latitude = SgRecord.MISSING

    longitude = SgRecord.MISSING
    hours_of_operation = SgRecord.MISSING

    try:
        page_url = "https://www.starbucks.com/store-locator/store/{}/{}".format(
            str(record["id"]), str(record["slug"])
        )
    except Exception:
        pass
    try:
        location_name = str(record["name"])
    except Exception:
        pass
    try:
        street_address = fix_comma(
            str(
                str(record["address"]["streetAddressLine1"])
                + ","
                + str(record["address"]["streetAddressLine2"])
                + ","
                + str(record["address"]["streetAddressLine3"])
            )
        )
    except Exception:
        pass

    try:
        city = str(record["address"]["city"])
    except Exception:
        pass

    try:
        state = str(record["address"]["countrySubdivisionCode"])
    except Exception:
        pass

    try:
        zip_postal = str(record["address"]["postalCode"])
    except Exception:
        pass

    try:
        country_code = str(record["address"]["countryCode"])
    except Exception:
        pass

    try:
        store_number = str(record["storeNumber"].split("-")[0])
    except Exception:
        pass

    try:
        phone = str(record["phoneNumber"])
    except Exception:
        pass

    try:
        location_type = str(
            str(record["brandName"]) + " - " + str(record["ownershipTypeCode"])
        )
    except Exception:
        pass

    try:
        latitude = str(record["coordinates"]["latitude"])
    except Exception:
        pass

    try:
        longitude = str(record["coordinates"]["longitude"])
    except Exception:
        pass

    try:
        hours_of_operation = format_hours(record["schedule"])
    except Exception:
        pass

    raw_address = SgRecord.MISSING

    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=clean(zip_postal),
        country_code=country_code,
        store_number=store_number,
        phone=clean(phone),
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        locator_domain="https://www.starbucks.com/",
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )


class ExampleSearchIteration(SearchIteration):
    def __init__(self):
        self.__state = CrawlStateSingleton.get_instance()

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

        with SgRequests() as http:
            lat, lng = coord
            url = str(
                f"https://www.starbucks.com/bff/locations?lat={round(lat,6)}&lng={round(lng,6)}&mop=true"
            )
            headers = {}
            headers["accept"] = "application/json"
            headers["accept-encoding"] = "gzip, deflate, br"
            headers["accept-language"] = "en-US,en;q=0.9,ro;q=0.8,es;q=0.7"
            headers["cache-control"] = "no-cache"
            headers["pragma"] = "no-cache"
            headers[
                "referer"
            ] = "https://www.starbucks.com/store-locator?map=39.21362,-105.911692,8z"
            headers[
                "sec-ch-ua"
            ] = '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"'
            headers["sec-ch-ua-mobile"] = "?0"
            headers["sec-ch-ua-platform"] = '"Windows"'
            headers["sec-fetch-dest"] = "empty"
            headers["sec-fetch-mode"] = "cors"
            headers["sec-fetch-site"] = "same-origin"
            headers[
                "user-agent"
            ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
            headers["x-requested-with"] = "XMLHttpRequest"
            try:
                locations = SgRequests.raise_on_err(
                    http.get(url, headers=headers)
                ).json()
                if locations["paging"]["total"] > 0:
                    for record in locations["stores"]:
                        try:
                            try:
                                found_location_at(
                                    record["coordinates"]["latitude"],
                                    record["coordinates"]["longitude"],
                                )
                            except Exception:
                                pass
                            yield ret_record(record)

                        except KeyError:
                            logzilla.error(f"Key error for record: {record}")

            except Exception as e:
                logzilla.error(f"Error on url: {url}", exc_info=e)


if __name__ == "__main__":
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_4()
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumAndPageUrlId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=SearchableCountries.ALL,
        )

        for rec in par_search.run():
            writer.write_row(rec)
