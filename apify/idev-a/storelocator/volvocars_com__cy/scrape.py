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

locator_domain = "https://www.volvocars.com/cy/"
base_url = "https://www.volvocars.com/cy/dealerships"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select_one("div.support-area").findChildren(recursive=False)[
            1:
        ]
        location_name = raw_address = phone = ""
        for _ in locations:
            if "Fax" in _.text or "Email" in _.text:
                continue
            if not location_name and _.strong:
                location_name = _.strong.text.strip()
            if "Address" in _.text:
                raw_address = list(_.stripped_strings)[1:]
            if "Tel" in _.text:
                phone = list(_.stripped_strings)[-1]
            if location_name and raw_address and phone:
                addr = parse_address_intl(", ".join(raw_address) + ", Cyprus")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                yield SgRecord(
                    page_url=base_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="Cyprus",
                    phone=phone,
                    locator_domain=locator_domain,
                    raw_address=", ".join(raw_address),
                )
                location_name = raw_address = phone = ""


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
