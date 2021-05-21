from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("yogenfruz")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def get_country_by_code(code=""):
    if code.isdigit():
        return "US"
    else:
        return "CA"


def _l(links, street_address):
    _link = ""
    for link in links:
        if link.select_one(".location-detail-address-1").text.strip() == street_address:
            _link = link.a["href"]
            break
    return _link


def fetch_data():
    locator_domain = "https://yogenfruz.com/"
    base_url = "https://yogenfruz.com/find-a-store/"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select(
            "div.location-search-results div.location-search-result .location-details-wrapper"
        )
        locations = soup.select("#location-singles .location-single")
        for _ in locations:
            phone = ""
            _phone = _.select_one("a.address-block-phone")
            if _phone:
                phone = _phone.text
            street_address = _.select_one("div.location_address").text
            if _.select_one("div.location_address-1"):
                street_address += " " + _.select_one("div.location_address-1").text
            city = state = ""
            _city_state = _.select_one("div.location_address-2")
            if _city_state:
                city = _city_state.text.split(",")[0].strip()
                state = _city_state.text.split(",")[1].strip()
            zip_postal = ""
            _zip = _.select_one("div.location-postal-code")
            if _zip:
                zip_postal = _zip.text
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in _.select("div.store-hours div.location-store-hours")
            ]
            hours_of_operation = "; ".join(hours)
            if "Hours vary" in hours_of_operation:
                hours_of_operation = ""
            coord = json.loads(
                _.select_one("div.location-map")["ng-init"]
                .split("initialize(")[1]
                .split(")")[0]
                .strip()
            )["center"]
            yield SgRecord(
                page_url=_l(links, street_address),
                store_number=_["id"].split("-")[-1],
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=coord["lat"],
                longitude=coord["lng"],
                country_code=get_country_by_code(zip_postal),
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
