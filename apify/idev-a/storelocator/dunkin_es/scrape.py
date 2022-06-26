from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dunkin.es"
base_url = "https://www.dunkin.es/localizador/"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.contenedor-lista-ubi ul li")
        for _ in locations:
            raw_address = _.p.text.strip()
            if not raw_address:
                continue
            addr = parse_address_intl(raw_address + ", Spain")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            street_address = street_address.replace("Spain", "").strip()
            if street_address.isdigit():
                street_address = raw_address.split(",")[0]
            city = addr.city
            if city == "N":
                city = ""
            try:
                coord = _.a["href"].split("/@")[1].split("/data")[0].strip()
            except:
                coord = ["", ""]
            bb = list(_.select_one("div.tel-hora").stripped_strings)
            hours_of_operation = ""
            phone = ""
            if bb:
                hours_of_operation = bb[-1]
                phone = _p(bb[0])
            yield SgRecord(
                page_url=base_url,
                location_name=_.h5.text.strip(),
                street_address=street_address,
                city=city,
                zip_postal=addr.postcode,
                country_code="Spain",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
