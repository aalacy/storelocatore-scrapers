from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import us
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("yogenfruz")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

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
        return "US"
    elif code in ca_provinces_codes:
        return "CA"
    else:
        return "<MISSING>"


def fetch_data():
    locator_domain = "https://yogenfruz.com/"
    base_url = "https://yogenfruz.com/find-a-store/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div.location-search-results div.location-search-result"
        )
        for _ in locations:
            logger.info(_.h3.a["href"])
            phone = ""
            _phone = _.select_one("a.address-block-phone")
            if _phone:
                phone = _phone.text
            sp1 = bs(session.get(_.h3.a["href"], headers=_headers).text, "lxml")
            street_address = sp1.select_one("div.location_address").text
            if sp1.select_one("div.location_address-1"):
                street_address += " " + sp1.select_one("div.location_address-1").text
            city = state = ""
            _city_state = sp1.select_one("div.location_address-2")
            if _city_state:
                city = _city_state.text.split(",")[0].strip()
                state = _city_state.text.split(",")[1].strip()
            zip_postal = ""
            _zip = sp1.select_one("div.location-postal-code")
            if _zip:
                zip_postal = _zip.text
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.store-hours div.location-store-hours")
            ]
            hours_of_operation = "; ".join(hours)
            if "Hours vary" in hours_of_operation:
                hours_of_operation = ""
            coord = json.loads(
                sp1.select_one("div.location-map")["ng-init"]
                .split("initialize(")[1]
                .split(")")[0]
                .strip()
            )["center"]
            yield SgRecord(
                page_url=_.h3.a["href"],
                store_number=_.h3.a["data-location"],
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=coord["lat"],
                longitude=coord["lng"],
                country_code=get_country_by_code(state),
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
