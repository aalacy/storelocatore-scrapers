from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.shell.eg"
base_url = "https://www.shell.eg/en_eg/business-customers/distributor-locator.html#iframe=L2Zvcm1zL2x1YnJpY2FudHNfc2ltcGxlX2VucXVpcnlfZWc"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("li.expandable-list__item")
        for _ in locations:
            _addr = [
                aa.text.replace("Distributor Address:", "")
                .replace("|", ", ")
                .replace("-", ",")
                for aa in _.select("ul li")[2:4]
            ]
            if "contact" in _addr[-1]:
                del _addr[-1]
            if "Person" in _addr[-1]:
                del _addr[-1]

            raw_address = " ".join(_addr)
            if raw_address and "Egypt" not in raw_address:
                raw_address = raw_address + ", Egypt"
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            try:
                phone = _.find("a", href=re.compile(r"tel:")).text.strip()
            except:
                phone = ""
            city = addr.city
            if not city:
                temp = (
                    _.select("ul li")[0]
                    .text.replace("Distributor Address:", "")
                    .strip()
                )
                if "locations" not in temp:
                    raw_address = temp
                    if raw_address and "Egypt" not in raw_address:
                        raw_address = raw_address + ", Egypt"
                    addr = parse_address_intl(raw_address)
                    city = addr.city
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Egypt",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.PHONE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
