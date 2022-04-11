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

locator_domain = "https://www.kipling.com.pe"
base_url = "https://www.kipling.com.pe/tiendas-kipling"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.stores_block")
        for _ in locations:
            raw_address = list(_.p.stripped_strings)[1]
            addr = parse_address_intl(raw_address + ", Peru")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = list(_.select("p")[2].stripped_strings)[1]
            hours = (
                " ".join(list(_.select("p")[1].stripped_strings))
                .replace("Horario de Atención:", "")
                .strip()
            )
            zip_postal = addr.postcode
            if zip_postal == "1":
                zip_postal = ""
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_postal,
                country_code="Peru",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
