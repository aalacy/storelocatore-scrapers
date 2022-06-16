from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("spar")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.spar.be"
base_url = "https://www.spar.be/winkels"


def fetch_data():
    urls = []
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.geolocation")
        for _ in locations:
            page_url = locator_domain + _.h2.a["href"]
            if page_url in urls:
                continue
            urls.append(page_url)
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            if res.status_code != 200:
                continue
            sp1 = bs(res.text, "lxml")
            raw_address = sp1.select_one(
                "div.field--name-field-store-address div.field__item"
            ).text
            addr = parse_address_intl(raw_address + ", Belgium")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = ""
            if sp1.select_one("div.field--name-field-store-telephone a"):
                phone = sp1.select_one("div.field--name-field-store-telephone a").text
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("table.office-hours__table tbody tr")
            ]
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Belgium",
                phone=phone,
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
