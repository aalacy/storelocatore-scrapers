from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://gloriajeans.ge"
base_url = "http://gloriajeans.ge/en/store-locator/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        _ = soup.select_one("div.wpsl-store-location")
        addr = list(_.p.stripped_strings)[-1].split(",")
        hours = [": ".join(hh.stripped_strings) for hh in _.select("table tr")]
        yield SgRecord(
            page_url=base_url,
            location_name=_.strong.text.strip(),
            street_address=" ".join(addr[1:]),
            city=addr[0].strip(),
            country_code="Georgia",
            phone=list(_.select_one("p.wpsl-contact-details").stripped_strings)[-1]
            .replace(":", "")
            .strip(),
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
            raw_address=", ".join(addr),
        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
