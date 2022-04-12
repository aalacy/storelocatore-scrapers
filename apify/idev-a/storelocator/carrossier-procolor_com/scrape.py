from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
import math
from concurrent.futures import ThreadPoolExecutor
import re

logger = SgLogSetup().get_logger("carrossier")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://carrossier-procolor.com/"
base_url = "https://www.procolor.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=50&search_radius=6000&filter={}&autoload=1"

country_map = {"us": "129", "ca": "128"}

max_workers = 24


def fetchConcurrentSingle(_):
    location_name = _["store"].replace("&#8217;", "'")
    slug = (
        location_name.lower()
        .replace("'", "")
        .replace("–", "")
        .replace(".", "")
        .replace("é", "e")
        .replace("è", "e")
        .replace("ô", "o")
        .replace("/", " ")
        .lower()
    )
    slug = "-".join([ss.strip() for ss in slug.split() if ss.strip()])
    if _["country"] == "Canada":
        page_url = f"https://www.procolor.com/fr-ca/atelier/{slug}/"
    else:
        page_url = f"https://www.procolor.com/en-us/shop/{slug}/"
    response = request_with_retries(page_url)
    return page_url, _, response


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    with SgRequests(proxy_country="us") as session:
        return session.get(url, headers=_headers)


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord,
        zipcode,
        current_country,
        items_remaining,
        found_location_at,
    ):
        lat = coord[0]
        lng = coord[1]
        with SgRequests(proxy_country="us") as session:
            _filter = country_map[current_country]
            url = base_url.format(lat, lng, _filter)
            try:
                locations = session.get(url, headers=_headers).json()
            except:
                return
            logger.info(f"[{current_country}] {len(locations)} found")
            for page_url, _, res in fetchConcurrentList(locations):
                found_location_at(_["lat"], _["lng"])
                hours = []
                if _["hours"]:
                    for hh in bs(_["hours"], "lxml").select("tr"):
                        day = hh.select("td")[0].text.strip()
                        times = list(hh.select("td")[1].stripped_strings)
                        hours.append(f"{day}: {', '.join(times)}")
                street_address = _["address"]
                if _["address2"]:
                    street_address += " " + _["address2"]
                logger.info(page_url)
                phone = _["phone"]
                if res.status_code == 200:
                    sp1 = bs(res.text, "lxml")
                    hours = []
                    for hh in sp1.select("div.working-hours div.row"):
                        day = hh.select_one("div.day").text.strip()
                        times = ", ".join(hh.select_one("div.hours").stripped_strings)
                        hours.append(f"{day}: {times}")
                    pp = sp1.find("a", href=re.compile(r"tel:"))
                    if not phone and pp:
                        phone = pp.text.strip()

                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["store"].replace("&#8217;", "'"),
                    street_address=street_address,
                    city=_["city"].strip(),
                    state=_["state"].strip(),
                    zip_postal=_["zip"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code=_["country"],
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours).replace("0013", "00, 13"),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        search_maker = DynamicSearchMaker(
            use_state=False,
            search_type="DynamicGeoSearch",
            expected_search_radius_miles=500,
        )
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        )

        for rec in par_search.run():
            writer.write_row(rec)
