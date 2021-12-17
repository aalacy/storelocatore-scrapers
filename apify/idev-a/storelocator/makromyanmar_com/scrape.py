from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.makromyanmar.com"
base_url = "https://www.makromyanmar.com/en/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.uael-modal-custom li a")
        for link in locations:
            page_url = locator_domain + link["href"]
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            raw_address = sp1.select_one("main div.uael-subheading").text.strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            coord = json.loads(sp1.select_one("div.uael-google-map")["data-locations"])[
                0
            ]
            yield SgRecord(
                page_url=page_url,
                location_name=" ".join(
                    sp1.select_one("main h3.uael-heading").stripped_strings
                ).replace("\n", ""),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Myanmar",
                phone=sp1.select("div.pp-info-list-description")[-1]
                .text.split("ext")[0]
                .strip(),
                latitude=coord[0],
                longitude=coord[1],
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
