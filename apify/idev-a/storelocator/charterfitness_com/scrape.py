from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

locator_domain = "https://www.charterfitness.com/"
json_url = "https://cfxfit.com/wp-admin/admin-ajax.php?action=store_search&lat=41.94045&lng=-88.14836&max_results=500&search_radius=5000&autoload=1"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            locations = session.get(json_url).json()
            for _ in locations:
                street_address = _.get("address")
                if _.get("address2"):
                    street_address += " " + _.get("address2")
                hours = []
                for hh in bs(_["hours"], "lxml").select("table tr"):
                    hours.append(": ".join(hh.stripped_strings))
                phone = _["phone"]
                if not phone:
                    driver.get(_.get("permalink"))
                    time.sleep(5)
                    sp1 = bs(driver.page_source, "lxml")
                    bb = list(
                        sp1.select("div.elementor-widget-container p")[
                            -1
                        ].stripped_strings
                    )
                    phone = _p(bb[-1])
                yield SgRecord(
                    page_url=_.get("permalink"),
                    store_number=_["id"],
                    location_name=_.get("store").replace("&#038;", "&"),
                    street_address=street_address,
                    city=_.get("city"),
                    state=_.get("state"),
                    zip_postal=_.get("zip"),
                    country_code=_.get("country", "USA"),
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=_["lat"],
                    longitude=_["lng"],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
