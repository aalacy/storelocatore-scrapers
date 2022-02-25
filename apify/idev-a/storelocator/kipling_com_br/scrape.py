from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.com.brs"
base_url = "https://www.kipling.com.br/institucional/nossas-lojas"


def fetch_data():
    with SgRequests() as http:
        soup = bs(http.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.endereco")
        for _ in locations:
            block = _.p.text.split(",")
            phone = ""
            if "@" in block[-1]:
                del block[-1]
            if "Tel" in block[-1]:
                phone = block[-1].split(":")[-1]
                del block[-1]
            raw_address = ", ".join(block)
            addr = parse_address_intl(raw_address + ", Brazil")
            location_name = "Kipling"
            name = _.h2.text.lower().strip()
            if "kipling" not in name:
                location_name = "Kipling Outlet"
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=block[0],
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Brazil",
                latitude=_.select_one("div.latitude").text.strip(),
                longitude=_.select_one("div.longitude").text.strip(),
                phone=phone,
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
