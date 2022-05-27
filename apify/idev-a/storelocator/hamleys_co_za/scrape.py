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

locator_domain = "https://www.hamleys.co.za/"
base_url = "https://www.hamleys.co.za/"


def _d(raw_address, name, phone):
    if "South Africa" not in raw_address:
        raw_address += ", South Africa"
    addr = parse_address_intl(raw_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    return SgRecord(
        page_url=base_url,
        location_name=name.strip(),
        street_address=street_address,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code="South Africa",
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.container.pt-3 div.col-sm-4")
        for _ in locations:
            if not _.text.strip():
                continue
            yield _d(
                _.p.text.strip(),
                _.h3.text.strip(),
                list(_.select("p")[1].stripped_strings)[-1],
            )

        bb = soup.select("div.form-subscribe-header")[1]
        yield _d(
            bb.select("p")[1].text.strip(),
            bb.select("h3")[1].text.strip(),
            list(bb.select("p")[2].stripped_strings)[-1],
        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
