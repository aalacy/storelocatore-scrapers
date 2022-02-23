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

locator_domain = "https://www.makro.com.br"
urls = {
    "Columbia": "https://makro.com.co/makro.php?id=CompraMakro#modal",
    "Brazil": "https://www.makro.com.br/comocomprar#",
    "Peru": "https://www.makro.pe/nuestras-tiendas",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            locations = soup.select("div.lojas")
            for _ in locations:
                if not _.text.strip():
                    continue
                block = list(_.stripped_strings)
                raw_address = block[1]
                addr = parse_address_intl(raw_address + ", " + country)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                phone = ""
                for bb in block:
                    if "Teléfono" in bb or "Telefone" in bb:
                        phone = bb.split(":")[-1].lower().split("anexo")[0]
                        break

                hours = [hh.text.strip() for hh in _.select("p2")]
                coord = _.a["onclick"].split("(")[-1].split(")")[0].split(",")
                yield SgRecord(
                    page_url=base_url,
                    location_name=_.p.text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    country_code=country,
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
