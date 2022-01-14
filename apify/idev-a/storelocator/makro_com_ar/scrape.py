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

locator_domain = "https://www.makro.com.ar"
base_url = "https://www.makro.com.ar/Como-comprar#local"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.lojas")
        for _ in locations:
            if not _.text.strip():
                continue
            block = list(_.stripped_strings)
            raw_address = block[1]
            _addr = raw_address.split(",")
            addr = parse_address_intl(raw_address + ", Argentina")
            street_address = _addr[0].split("(")[0].split("-")[0].strip()
            phone = ""
            for bb in block:
                if "Teléfono" in bb or "Telefone" in bb:
                    phone = bb.split(":")[-1]
                    break

            hours = [hh.text.strip() for hh in _.select("p2")]
            coord = _.a["onclick"].split("(")[-1].split(")")[0].split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=_.p.text.strip(),
                street_address=street_address,
                city=_addr[-1].split("-")[0].strip(),
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Argentina",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
