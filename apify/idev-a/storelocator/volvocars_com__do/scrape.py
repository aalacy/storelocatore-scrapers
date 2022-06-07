from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.volvocars.com/do/"
base_url = "https://www.volvocars.com/do/services/design-and-buy/find-a-dealer"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.support-area p")
        location_name = ""
        for _ in locations:
            if "cta-container" not in _.find_next_sibling().get("class", []):
                continue
            block = list(_.stripped_strings)
            raw_address = block[0]
            addr = parse_address_intl(raw_address + ", Dominican Republic")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if _.find_previous_sibling("p").strong:
                location_name = (
                    _.find_previous_sibling("p").strong.text.replace(":", "").strip()
                )
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Dominican Republic",
                phone=block[1].split(":")[-1].strip(),
                locator_domain=locator_domain,
                hours_of_operation="",
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
