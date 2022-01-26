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

locator_domain = "https://gloriajeans.co.uk"
base_url = "https://gloriajeans.co.uk/stores/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select('div[role="main"] div.medium-6')
        for _ in locations:
            if not _.text.strip() or "opening soon" in _.h3.text:
                continue
            block = list(
                _.select(".wpb_text_column.wpb_content_element")[1].stripped_strings
            )
            hours = ""
            addr = block
            if "Hour" in block[-1]:
                hours = block[-1].replace("Hours:", "")
                addr = block[:-1]

            zip_postal = addr[-1].strip()
            raw_address = " ".join(addr)
            addr = parse_address_intl(raw_address + ", United Kingdom")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_postal,
                country_code="UK",
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
