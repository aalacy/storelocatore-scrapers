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

locator_domain = "https://www.lezap.be"
base_url = "https://www.lezap.be/magasins"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.col-xs-12.col-sm-10")
        for _ in locations:
            block = list(_.select_one("div.col-xs-12 p").stripped_strings)
            phone = ""
            _addr = []
            for x, bb in enumerate(block):
                if "Tél" in bb:
                    phone = bb.replace("Tél", "").split(":")[-1].strip()
                    _addr = block[:x]
                    break
            raw_address = " ".join(_addr)
            addr = parse_address_intl(raw_address + ", Belgium")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            hours = []
            for hh in _.select("div.col-xs-12")[1].select("p"):
                hours.append(" ".join(hh.stripped_strings))
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="BE",
                phone=phone,
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
