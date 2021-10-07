from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("lavieenrose")

locator_domain = "https://www.lavieenrose.com"
base_url = "https://www.lavieenrose.com/en/our-stores"
loc_url = "/en/our-stores/SearchStores"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    if (
        val.replace("(", "")
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
        with SgRequests() as http:
            driver.get(base_url)
            rr = driver.wait_for_request(loc_url, timeout=15)
            headers = {}
            for key, val in rr.headers.items():
                if key != "accept-encoding":
                    headers[key] = val
            locations = bs(
                http.post(rr.url, headers=headers, data=rr.body).text, "lxml"
            ).select("div.js-store-tile")
            for _ in locations:
                location_type = "outlets"
                if (
                    "boutique"
                    in _.select_one("div.tmx-store-tile-index img")["data-src"].lower()
                ):
                    location_type = "boutique"
                page_url = _.select_one("div.direction-container div a")["href"]
                logger.info(page_url)
                sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
                hours = []
                for hh in sp1.select("div.js-container-details-0")[0].select("div.row"):
                    div = list(hh.stripped_strings)
                    hours.append(f"{div[0]}: {div[1]} - {div[2]}")
                _addr = list(
                    sp1.select_one("div.tmx-store-address span").stripped_strings
                )
                info = _.select_one("div.favorite-store-icon-container div")
                raw_address = _.select_one("div.direction-container a.store-link")[
                    "data-address"
                ].replace("+", ",")
                addr = raw_address.split(",")
                yield SgRecord(
                    page_url=page_url,
                    store_number=info["id"],
                    location_name=_.select_one("div.store-title").text.strip(),
                    street_address=" ".join(addr[:-3]),
                    city=addr[-3],
                    state=addr[-2],
                    zip_postal=_addr[1].split()[-1],
                    latitude=info["data-lat"],
                    longitude=info["data-lng"],
                    country_code=addr[-1],
                    phone=_p(_.select_one("a.store-link").text.strip()),
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    location_type=location_type,
                    raw_address=" ".join(_addr),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
