from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefour.ci"
base_url = "https://www.carrefour.ci/nos-magasins/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("article div.wp-block-columns div.wp-block-column")
        for _ in locations:
            if not _.text.strip():
                continue
            raw_address = list(_.p.stripped_strings)[0]
            addr = raw_address.split()
            location_name = _.h3.text.strip()
            location_type = ""
            if "Carrefour Marcory" in location_name:
                location_type = "Carrefour Marcory"
            elif "Carrefour Market" in location_name:
                location_type = "Carrefour Market"
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=", ".join(addr[:-1]),
                city=addr[-1],
                country_code="Ivory Coast",
                location_type=location_type,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
