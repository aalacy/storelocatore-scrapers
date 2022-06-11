from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling.com.co"
base_url = "https://www.kipling.com.co/info/localizador-de-tiendas"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.localizador_desktop table tr")[1:]
        for _ in locations:
            td = _.select("td")
            raw_address = td[1].text.strip()
            addr = parse_address_intl(raw_address)
            yield SgRecord(
                page_url=base_url,
                location_name="Kipling",
                street_address=raw_address.split(",")[0],
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Colombia",
                phone=td[2].text.strip().split("Ext")[0],
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(td[-1].stripped_strings),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
