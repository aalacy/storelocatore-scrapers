from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.baskinrobbins.com.my"
base_url = "https://www.baskinrobbins.com.my/content/baskinrobbins/en/location.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("ul#myUL li")
        for _ in locations:
            raw_address = (
                _.h5.find_next_sibling("p")
                .text.replace("\n", " ")
                .replace("\r", "")
                .strip()
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            name = list(_.h5.stripped_strings)
            _p = list(_.select_one("p.availability").stripped_strings)
            if _p[0] != "Tel:":
                del _p[0]
            phone = _p[1]
            if phone == "N/A":
                phone = ""
            yield SgRecord(
                page_url=base_url,
                location_name=name[0],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="MY",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.PHONE, SgRecord.Headers.CITY}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
