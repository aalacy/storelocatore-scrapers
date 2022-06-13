from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import Grain_2
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("newbalance_com")

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
locator_domain = "https://www.newbalance.com/"


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:
        with SgRequests(proxy_country="us") as session:
            x = coord[0]
            y = coord[1]
            url = (
                "https://newbalance.locally.com/stores/conversion_data?has_data=true&company_id=41&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat="
                + str(x)
                + "&map_center_lng="
                + str(y)
                + "&map_distance_diag=100&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=&zoom_level=10"
            )
            res_json = session.get(url, headers=HEADERS).json()["markers"]

            logger.info(f"[{current_country}] [{x, y}] {len(res_json)}")

            for loc in res_json:
                found_location_at(loc["lat"], loc["lng"])
                if "New Balance" in loc["name"]:
                    location_name = loc["name"]

                    slug = loc["slug"]
                    if slug == "":
                        page_url = (
                            "https://stores.newbalance.com/shop/"
                            + str(loc["id"])
                            + "/"
                            + location_name.lower().split("|")[0].replace(" ", "-")
                        )
                    else:
                        page_url = "https://stores.newbalance.com/shop/" + slug

                    try:
                        cat = (
                            str(loc["enhanced_categories"])
                            .split(":")[0]
                            .replace("{", "")
                            .replace("'", "")
                        )
                        location_type = loc["enhanced_categories"][cat]["value"]
                    except:
                        location_type = "<MISSING>"

                    hours = []
                    if page_url != "https://stores.newbalance.com/shop/new-balance":
                        soup = BeautifulSoup(
                            session.get(page_url, headers=HEADERS).content, "lxml"
                        )
                        loc_json = json.loads(
                            soup.find("script", {"type": "application/ld+json"}).text
                        )
                        for hh in loc_json.get("openingHoursSpecification", []):
                            hours.append(
                                f"{', '.join(hh['dayOfWeek'])}: {hh['opens']} - {hh['closes']}"
                            )

                    yield SgRecord(
                        page_url=page_url,
                        locator_domain=locator_domain,
                        location_name=location_type,
                        street_address=loc["address"].split("--- ")[-1].strip(),
                        city=loc["city"],
                        state=loc["state"],
                        zip_postal=loc["zip"],
                        country_code=loc["country"],
                        latitude=loc["lat"],
                        longitude=loc["lng"],
                        phone=loc["phone"].replace("tel:", "").strip(),
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_2()
    )

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=[
                "ca",
                "us",
                "gb",
                "ie",
                "at",
                "nl",
                "dk",
                "ee",
                "lt",
                "si",
                "fi",
                "lv",
                "lu",
                "be",
                "fr",
                "it",
                "pt",
                "es",
                "de",
            ],
        )

        for rec in par_search.run():
            writer.write_row(rec)
