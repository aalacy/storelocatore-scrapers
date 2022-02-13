from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("chompies")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://chompies.com"
base_url = "https://chompies.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxRqlWqBQCnUQoG"
page_url = "https://chompies.com/contact/"


def _pp(locs, address):
    for loc in locs:
        if not loc.h4 and not loc.p:
            continue
        if " ".join(address.split()[:2]) in list(loc.p.stripped_strings)[0]:
            return loc


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["markers"]
        locs = bs(session.get(page_url, headers=_headers).text, "lxml").select(
            "div.so-panel.widget"
        )
        for _ in locations:
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            loc = _pp(locs, _["address"])
            if not loc:
                import pdb

                pdb.set_trace()
            phone = ""
            if loc.strong.a:
                phone = loc.strong.a.text.strip()
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=loc.h4.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
