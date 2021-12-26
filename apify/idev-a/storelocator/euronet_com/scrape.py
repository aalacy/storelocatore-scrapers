from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import bs4
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.euronetworldwide.com"
base_url = "https://www.euronetworldwide.com/about-euronet/our-locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "main div.elementor-toggle-item div.elementor-tab-content"
        )

        for loc in locations:
            location_name = phone = ""
            _addr = []
            country_code = loc.find_previous_sibling("div").text.strip()
            for x, _ in enumerate(loc.contents):
                if not location_name and _.name == "strong":
                    location_name = _.text.replace("\n", " ").strip()
                if (
                    isinstance(_, bs4.element.NavigableString)
                    and "T:" in _.previous_element
                ):
                    phone = _.strip()

                if (
                    location_name
                    and not phone
                    and isinstance(_, bs4.element.NavigableString)
                    and _.strip()
                ):
                    _addr.append(_.strip())

                if location_name and (_.name == "hr" or x == len(loc.contents) - 1):
                    raw_address = " ".join(_addr).replace(
                        "Kingdom of Bahrain", "Bahrain"
                    )
                    addr = parse_address_intl(raw_address)
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
                        country_code=country_code,
                        phone=phone.replace("(Help Desk)", "").split("ext")[0].strip(),
                        locator_domain=locator_domain,
                        raw_address=" ".join(_addr),
                    )

                    location_name = phone = ""
                    _addr = []


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
