from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.gloriajeanscoffees.my"
base_url = "http://www.gloriajeanscoffees.my/our-store"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div.uk-section-default > div > div.uk-container div.tm-grid-expand"
        )
        for _ in locations:
            if not _.h2:
                continue
            raw_address = " ".join(_.p.stripped_strings)
            addr = parse_address_intl(raw_address + ", Malaysia")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if not street_address:
                street_address = raw_address.split(",")[0].strip()
            hours = [": ".join(hh.stripped_strings) for hh in _.select("ul.uk-list li")]
            ss = json.loads(_.find("script", type="application/json").string)[
                "markers"
            ][0]
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="MY",
                latitude=ss["lat"],
                longitude=ss["lng"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
