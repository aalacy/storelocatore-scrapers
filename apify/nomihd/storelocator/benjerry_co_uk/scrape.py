from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import Grain_8
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "benjerry.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)


class _SearchIteration(SearchIteration):
    """
    Here, you define what happens with each iteration of the search.
    The `do(...)` method is what you'd do inside of the `for location in search:` loop
    It provides you with all the data you could get from the search instance, as well as
    a method to register found locations.
    """

    def __init__(self, http: SgRequests):
        self.__http = http
        self.__state = CrawlStateSingleton.get_instance()

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        log.info(f"pulling data for zipcode: {zipcode}")
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            payload = "addressline=" + str(zipcode) + "&icons=SHOP%2Cdefault%2CCINEMA"

            r = SgRequests.raise_on_err(
                self.__http.post(
                    "https://www.benjerry.co.uk/home/scoop-shops/main/scoopshopcontent/genericContent/brand-redesign-header-grid/columnOne/scoop-shop--header.where2GetItActionNew.do",
                    headers=headers,
                    data=payload,
                )
            )
            json_data = r.json()
            if "collection" in json_data["response"]:

                if isinstance(json_data["response"]["collection"]["poi"], list):
                    for data in json_data["response"]["collection"]["poi"]:
                        locator_domain = website
                        location_name = data["name"]
                        log.info(location_name)
                        street_address = data["address1"]

                        if data["address2"]:
                            street_address += ", " + data["address2"]
                        city = data["city"]
                        state = json_data["response"]["collection"]["province"]
                        zip = data["postalcode"]
                        location_type = data["icon"]
                        phone = data["phone"]
                        try:
                            if len(phone) <= 0:
                                phone = "<MISSING>"
                        except:
                            pass

                        if data["country"] != "UK":
                            continue
                        country_code = data["country"]
                        latitude = data["latitude"]
                        longitude = data["longitude"]
                        hours = ""
                        if data["monday"]:
                            hours += "Monday" + " " + data["monday"]
                        else:
                            hours += "Monday Closed"

                        if data["tuesday"]:
                            hours += " " + "Tuesday" + " " + data["tuesday"]
                        else:
                            hours += " " + "Tuesday Closed"

                        if data["wednesday"]:
                            hours += " " + "Wednesday" + " " + data["wednesday"]
                        else:
                            hours += " " + "Wednesday Closed"

                        if data["thursday"]:
                            hours += " " + "Thursday" + " " + data["thursday"]
                        else:
                            hours += " " + "Thursday Closed"

                        if data["friday"]:
                            hours += " " + "Friday" + " " + data["friday"]
                        else:
                            hours += " " + "Friday Closed"

                        if data["saturday"]:
                            hours += " " + "Saturday" + " " + data["saturday"]
                        else:
                            hours += " " + "Saturday Closed"

                        if data["sunday"]:
                            hours += " " + "Sunday" + " " + data["sunday"]
                        else:
                            hours += " " + "Sunday Closed"

                        if hours.count("Closed") == 7:
                            hours = "<MISSING>"

                        page_url = "<MISSING>"
                        if data["subdomain"]:
                            page_url = "https://www.benjerry.co.uk/" + str(
                                data["subdomain"]
                            )
                        else:
                            page_url = "<MISSING>"

                        store_number = data["uid"]
                        yield SgRecord(
                            locator_domain=locator_domain,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zip,
                            country_code=country_code,
                            store_number=store_number,
                            phone=phone,
                            location_type=location_type,
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation=hours,
                        )

                else:
                    data = json_data["response"]["collection"]["poi"]
                    locator_domain = website
                    location_name = data["name"]
                    log.info(location_name)
                    street_address = data["address1"]

                    if data["address2"]:
                        street_address += ", " + data["address2"]
                    city = data["city"]
                    state = json_data["response"]["collection"]["province"]
                    zip = data["postalcode"]
                    location_type = data["icon"]
                    phone = data["phone"]
                    try:
                        if len(phone) <= 0:
                            phone = "<MISSING>"
                    except:
                        pass
                    country_code = data["country"]

                    latitude = data["latitude"]
                    longitude = data["longitude"]

                    hours = ""
                    if data["monday"]:
                        hours += "Monday" + " " + data["monday"]
                    else:
                        hours += "Monday Closed"

                    if data["tuesday"]:
                        hours += " " + "Tuesday" + " " + data["tuesday"]
                    else:
                        hours += " " + "Tuesday Closed"

                    if data["wednesday"]:
                        hours += " " + "Wednesday" + " " + data["wednesday"]
                    else:
                        hours += " " + "Wednesday Closed"

                    if data["thursday"]:
                        hours += " " + "Thursday" + " " + data["thursday"]
                    else:
                        hours += " " + "Thursday Closed"

                    if data["friday"]:
                        hours += " " + "Friday" + " " + data["friday"]
                    else:
                        hours += " " + "Friday Closed"

                    if data["saturday"]:
                        hours += " " + "Saturday" + " " + data["saturday"]
                    else:
                        hours += " " + "Saturday Closed"

                    if data["sunday"]:
                        hours += " " + "Sunday" + " " + data["sunday"]
                    else:
                        hours += " " + "Sunday Closed"

                    if hours.count("Closed") == 7:
                        hours = "<MISSING>"

                    page_url = "<MISSING>"
                    if data["subdomain"]:
                        page_url = "https://www.benjerry.co.uk/" + str(
                            data["subdomain"]
                        )
                    else:
                        page_url = "<MISSING>"

                    store_number = data["uid"]
                    if data["country"] != "UK":
                        log.info("country other than UK")
                    else:
                        yield SgRecord(
                            locator_domain=locator_domain,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zip,
                            country_code=country_code,
                            store_number=store_number,
                            phone=phone,
                            location_type=location_type,
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation=hours,
                        )
        except:
            pass


def scrape():
    log.info("Started")
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicZipSearch",
        expected_search_radius_miles=50,
    )

    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests(dont_retry_status_codes=([404])) as http:
            search_iter = _SearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=["GB"],
            )

            for rec in par_search.run():
                writer.write_row(rec)


if __name__ == "__main__":
    scrape()
