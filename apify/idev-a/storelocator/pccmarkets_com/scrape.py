from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

locator_domain = "https://www.pccmarkets.com/"
base_url = "https://www.pccmarkets.com/stores/"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url).text, "lxml").select(
            'div[data-js="google-map-marker"]'
        )
        for _ in locations:
            addr = list(_.address.stripped_strings)
            phone = ""
            if _.find("a", href=re.compile(r"tel:")):
                phone = _.find("a", href=re.compile(r"tel:")).text.strip()
            _hr = _.find("strong", string=re.compile(r"Store hours"))
            hours = ""
            if _hr:
                hours = _hr.find_next_sibling().text.strip()
            yield SgRecord(
                page_url=_.select_one("a.pcc-link-cta")["href"],
                location_name=_.h4.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                country_code="US",
                phone=phone,
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
