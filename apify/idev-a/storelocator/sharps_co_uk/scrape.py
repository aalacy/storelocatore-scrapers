from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://www.sharps.co.uk/fitted-bedroom-showroom-locator",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.sharps.co.uk"
base_url = "https://www.sharps.co.uk/fitted-bedroom-showroom-locator"
json_url = "https://www.sharps.co.uk/api/showrooms/listing/"


def fetch_data():
    with SgRequests() as session:
        _headers["x-api-key"] = bs(
            session.get(base_url, headers=_headers).text, "lxml"
        ).select_one('meta[name="csrf"]')["content"]
        locations = session.get(json_url, headers=_headers).json()
        for _ in locations:
            _addr = " ".join(bs(_["address"], "lxml").stripped_strings)
            addr = parse_address_intl(_addr + ", United Kingdom")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in bs(_["openingTimes"], "lxml").select("tr")
            ]
            yield SgRecord(
                page_url=_["url"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="UK",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_addr,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
