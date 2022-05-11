from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton, SerializableRequest
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_8
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import sglog
from sgscrape import sgpostal as parser
from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait  # noqa
from selenium.webdriver.common.by import By  # noqa
from selenium.webdriver.support import expected_conditions as EC  # noqa
from selenium.webdriver.common.keys import Keys  # noqa
from bs4 import BeautifulSoup as b4

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


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


def ret_record(soup, url, lat, lng):

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
    raw_address = SgRecord.MISSING
    latitude = lat if lat else SgRecord.MISSING
    longitude = lng if lng else SgRecord.MISSING

    try:
        page_url = url
    except Exception:
        pass
    try:
        location_name = soup.find("title").text.strip()
    except Exception:
        pass
    try:
        try:
            raw_address = soup.find("address").find("a").text.strip()
        except Exception:
            raw_address = soup.find("address").text.strip()
    except Exception:
        pass
    parsed = parser.parse_address_intl(raw_address)
    try:
        street_address = (
            parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        )
        street_address(
            (street_address + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street_address
        )
    except Exception:
        pass

    try:
        city = parsed.city if parsed.city else SgRecord.MISSING
    except Exception:
        pass

    try:
        state = parsed.state if parsed.state else SgRecord.MISSING
    except Exception:
        pass

    try:
        zip_postal = parsed.postcode if parsed.postcode else SgRecord.MISSING
    except Exception:
        pass

    try:
        country_code = parsed.country if parsed.country else SgRecord.MISSING
    except Exception:
        pass

    try:
        phone = soup.find(
            "a", {"href": lambda x: x and x.startswith("tel:")}
        ).text.strip()
    except Exception:
        pass

    try:
        coords = (
            soup.find("a", {"href": lambda x: x and "google.com/maps?q=" in x})["href"]
            .split("google.com/maps?q=", 1)[1]
            .split(",")
        )
    except Exception:
        coords = [SgRecord.MISSING, SgRecord.MISSING]
    if not latitude or latitude == SgRecord.MISSING:
        latitude = coords[0]
    if not longitude or longitude == SgRecord.MISSING:
        longitude = coords[1]

    try:
        hours_of_operation = "; ".join(
            list(
                soup.find(
                    "ol", {"class": lambda x: x and "opening-times" in x}
                ).stripped_strings
            )
        )
    except Exception:
        pass

    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        locator_domain="https://toniandguy.com/",
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

        with SgChrome() as driver:
            lat, lng = coord
            url = "https://toniandguy.com/salon-finder"
            driver.get(url)
            searchbox_xpath = '//*[@id="content"]/main/section/section/div/div/div/form/div/div[1]/input'  # Might break
            inputel = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, searchbox_xpath))
            )
            inputel.send_keys(f"{lat}, {lng}")
            inputel.send_keys(Keys.ENTER)
            soup = b4(driver.page_source, "lxml")
            locs = soup.find_all("div", {"data-map-marker": True})
            for loc in locs:
                data = loc["data-map-marker"].split(",")
                try:
                    found_location_at(
                        data[0],
                        data[1],
                    )
                except Exception:
                    pass
                yield {"lat": data[0], "lng": data[1], "link": data[-1]}


def fetch_records(http, state):
    for next_r in state.request_stack_iter():
        lat = next_r.context.get("lat")
        lng = next_r.context.get("lng")
        url = next_r.url
        page = SgRequests.raise_on_err(http.get(url))
        try:
            soup = b4(page.text, "lxml")
            return ret_record(soup, url, lat, lng)
        except Exception:
            return ret_record(None, url, lat, lng)


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_8()
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=SearchableCountries.ALL,
        )

        def record_initial_requests(par_search, state):
            for rec in par_search.run():
                state.push_request(
                    SerializableRequest(
                        url=rec["link"], context={"lat": rec["lat"], "lng": rec["lng"]}
                    )
                )

        state.get_misc_value(
            "init", default_factory=lambda: record_initial_requests(par_search, state)
        )

        with SgRequests() as http:
            for rec in fetch_records(http, state):
                writer.write_row(rec)
