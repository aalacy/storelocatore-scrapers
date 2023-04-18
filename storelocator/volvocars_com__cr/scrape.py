from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.volvocars.com/cr"
base_url = "https://www.volvocars.com/cr/v/legal/contact-us"


def fetch_data():
    with SgRequests() as session:
        locations = []
        for ss in bs(session.get(base_url, headers=_headers).text, "lxml").find_all(
            "script", type="application/json"
        ):
            if "sitecore" in json.loads(ss.text):
                locations = bs(
                    json.loads(ss.text)["sitecore"]["route"]["placeholders"][
                        "article-section"
                    ][0]["fields"]["body"]["value"],
                    "lxml",
                ).select("p")[3:-1]
                break
        for _ in locations:
            block = list(_.stripped_strings)
            _addr = []
            phone = ""
            for x, bb in enumerate(block):
                if "Direcci" in bb:
                    new_b = block[x + 1 :]
                    for y, cc in enumerate(new_b):
                        if "Tel" in cc:
                            phone = new_b[y + 1]
                            break
                        _addr.append(cc)
                    break

            raw_address = " ".join(_addr)
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                location_name=_.strong.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CR",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
