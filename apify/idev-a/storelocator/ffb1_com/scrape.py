from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("ffb1")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.ffb1.com"
base_url = "https://www.ffb1.com/about-us/locations-hours.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul#locList li")
        for _ in locations:
            street_address = _["data-address1"]
            if _["data-address2"]:
                street_address += " " + _["data-address2"]
            if street_address == "NA":
                street_address = ""
            location_type = "branch"
            if _.select_one("span.hasATM"):
                location_type += ", atm"
            if "ATM Only" in _["data-title"]:
                location_type = "atm"
            page_url = ""
            if _.select_one("a.seeDetails"):
                page_url = locator_domain + _.select_one("a.seeDetails")["href"]
            _p = _.find("span", string=re.compile(r"Phone"))
            phone = ""
            if _p:
                phone = _p.find_next_sibling().text.strip()
            _hr = _.select_one("div.hours .lobbyHours")
            hours = ""
            if _hr:
                hours = ": ".join(_hr.select_one("div").stripped_strings)
            yield SgRecord(
                page_url=page_url,
                location_name=_["data-title"].replace("–", "-"),
                street_address=street_address.replace("Prospect Building", "").strip(),
                city=_["data-city"],
                state=_["data-state"],
                zip_postal=_["data-zip"],
                country_code="CA",
                latitude=_["data-latitude"],
                longitude=_["data-longitude"],
                phone=phone,
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=hours.replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_TYPE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
