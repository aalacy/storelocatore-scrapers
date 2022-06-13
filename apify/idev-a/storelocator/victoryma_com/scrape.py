from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re
import us
from sgpostal.sgpostal import parse_address_intl
from tenacity import retry, wait_random, stop_after_attempt

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.victoryma.com"
base_url = "https://www.victoryma.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=100&search_radius=3000"

coords = [("39.47", "-0.36"), ("-33.62", "150.83"), ("28.43", "-81.26")]
ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


def get_country_by_code(code=""):
    if us.states.lookup(code):
        return "United States"
    elif code in ca_provinces_codes:
        return "CA"
    else:
        return "<MISSING>"


@retry(stop=stop_after_attempt(7), wait=wait_random(min=10, max=30))
def _info(_):
    hours = []
    _addr = []
    with SgRequests(proxy_country="us") as session:
        sp1 = bs(session.get(_["url"], headers=_headers).text, "lxml")
        _hr = sp1.find("span", string=re.compile(r"^HOURS$"))
        if _hr:
            days = list(
                _hr.find_parent("h2")
                .find_next_sibling()
                .select_one("div.col-4")
                .stripped_strings
            )
            times = list(
                _hr.find_parent("h2")
                .find_next_sibling()
                .select_one("div.col-8")
                .stripped_strings
            )
            for x in range(len(days)):
                hours.append(f"{days[x]}: {times[x]}")

        try:
            _addr = list(
                sp1.select_one("div.vs15-content.order-sm-1 h3").stripped_strings
            )
        except:
            pass
    raw_address = ", ".join(_addr)
    addr = parse_address_intl(raw_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2

    zip_postal = _["zip"] or addr.postcode
    if not zip_postal:
        logger.warning(f'exception in zip_postal {_["url"]} {zip_postal}')
        raise Exception

    return (
        hours,
        raw_address,
        street_address,
        addr.state,
        zip_postal,
    )


def fetch_data():
    for lat, lng in coords:
        with SgRequests(proxy_country="us") as session:
            locations = session.get(base_url.format(lat, lng), headers=_headers).json()
            logger.info(f"[{lat, lng}] {len(locations)}")
            for _ in locations:
                logger.info(_["url"])
                hours = []
                street_address = raw_address = _state = zip_postal = ""
                if _["url"]:
                    hours, raw_address, street_address, _state, zip_postal = _info(_)

                hours_of_operation = "; ".join(hours)
                if hours_of_operation:
                    hours_of_operation = hours_of_operation.split("(")[0]
                country_code = _["country"]
                state = _["state"] or _state
                if country_code not in ["Spain", "United States", "Australia"]:
                    state = _["store"].split(",")[-1].strip()
                    country_code = get_country_by_code(state)

                if not street_address:
                    street_address = _["address"]
                    if _["address2"]:
                        street_address += " " + _["address2"]

                yield SgRecord(
                    page_url=_["url"],
                    store_number=_["id"],
                    location_name=_["store"].replace("&#8211;", "-"),
                    street_address=street_address,
                    city=_["city"].replace(",", "").split("/")[0],
                    state=state,
                    zip_postal=zip_postal,
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code=country_code,
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
