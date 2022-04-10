from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup

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
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
        }

        params = (
            ("lang", "en_US"),
            (
                "xml_request",
                f'<request><appkey>3D71930E-EC80-11E6-A0AE-8347407E493E</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>10000</limit><geolocs><geoloc><addressline>{zipcode}</addressline><longitude></longitude><latitude></latitude><country>UK</country></geoloc></geolocs><searchradius>100</searchradius><order>RANK, _distance</order><stateonly>1</stateonly><radiusuom></radiusuom><proximitymethod>drivetime</proximitymethod><cutoff>500</cutoff><cutoffuom>mile</cutoffuom><distancefrom>0.01</distancefrom><where><or><curbside><eq></eq></curbside><cakesforsale><eq></eq></cakesforsale><catering><eq></eq></catering><fcd><eq></eq></fcd><flavorserved><eq></eq></flavorserved></or><icon><in>Shop,SHOP,shop,CINEMA,Cinema,default</in></icon><clientkey><notin></notin></clientkey></where></formdata></request>',
            ),
        )

        try:
            r = SgRequests.raise_on_err(
                self.__http.get(
                    "https://benjerry.where2getit.com/ajax",
                    params=params,
                    headers=headers,
                )
            )
            soup = BeautifulSoup(r.text, "lxml")
            locator_domain = "benjerry.co.uk"
            location_name = ""
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = "<MISSING>"
            location_type = "benjerry"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"
            page_url = "<MISSING>"

            for script in soup.find_all("poi"):

                location_name = script.find("name").text
                log.info(location_name)
                street_address = script.find("address1").text
                page_url = script.find("subdomain").text
                if len(page_url) > 0:
                    page_url = "https://www.benjerry.co.uk/" + page_url

                if len(script.find("address2").text) > 0:
                    street_address = street_address + "," + script.find("address2").text

                city = script.find("city").text
                state = script.find("state").text
                zipp = script.find("postalcode").text
                if "00000" == zipp:
                    zipp = "<MISSING>"
                country_code = script.find("country").text
                if country_code != "UK":
                    continue
                latitude = script.find("latitude").text
                longitude = script.find("longitude").text
                phone = script.find("phone").text.replace("&#xa0;", "")
                location_type = script.find("icon").text.strip()
                store_number = script.find("clientkey").text

                if "n/a" in phone:
                    phone = "<MISSING>"

                if (
                    len(script.find("sunday").text) > 0
                    or len(script.find("monday").text) > 0
                    or len(script.find("tuesday").text) > 0
                    or len(script.find("wednesday").text) > 0
                    or len(script.find("thursday").text) > 0
                    or len(script.find("friday").text) > 0
                    or len(script.find("saturday").text) > 0
                ):
                    hours_of_operation = (
                        "Sunday : "
                        + script.find("sunday").text
                        + "; "
                        + "Monday : "
                        + script.find("monday").text
                        + "; "
                        + "Tuesday : "
                        + script.find("tuesday").text
                        + "; "
                        + "Wednesday : "
                        + script.find("wednesday").text
                        + "; "
                        + "Thursday : "
                        + script.find("thursday").text
                        + "; "
                        + "Friday : "
                        + script.find("friday").text
                        + "; "
                        + "Saturday : "
                        + script.find("saturday").text
                    )
                else:
                    hours_of_operation = "<MISSING>"

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
        except:
            pass


def scrape():
    log.info("Started")
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicZipSearch",
        expected_search_radius_miles=100,
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
