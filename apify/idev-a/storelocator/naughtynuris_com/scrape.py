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

locator_domain = "https://naughtynuris.com"
base_url = "https://naughtynuris.com/international"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        blocks = soup.select("div.agile-about-top div.content > div")
        for block in blocks:
            name = raw_address = phone = ""
            for ch in block.findChildren(recursive=False):
                _cc = ch.text.strip()
                if _cc == ":" or "Coming Soon" in _cc:
                    continue

                if ch.name == "div":
                    country = ch.find_previous_siblings("h3")[0].text.strip()
                    if not name and ch["class"] == ["col-xs-12"]:
                        name = _cc
                    if ch["class"] == ["col-xs-10", "left"]:
                        raw_address = _cc
                    elif ch["class"] == ["col-xs-10"]:
                        phone = _cc
                    if name and raw_address and phone:
                        addr = parse_address_intl(raw_address + ", " + country)
                        street_address = addr.street_address_1
                        if addr.street_address_2:
                            street_address += " " + addr.street_address_2
                        yield SgRecord(
                            page_url=base_url,
                            location_name=name,
                            street_address=street_address,
                            city=addr.city,
                            state=addr.state,
                            zip_postal=addr.postcode,
                            country_code=country,
                            phone=phone,
                            locator_domain=locator_domain,
                            raw_address=raw_address,
                        )

                        name = raw_address = phone = ""


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
