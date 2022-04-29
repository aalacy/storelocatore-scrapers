from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("atlantic")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.atlantic.caa.ca"
base_url = "https://www.atlantic.caa.ca/locations.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "section.Section.Section--twoColMatch  div.generic-container"
        )
        for _ in locations:
            addr = list(_.p.stripped_strings)
            _pp = _.find("", string=re.compile(r"Phone:"))
            phone = ""
            if _pp:
                phone = _pp.split(":")[-1].strip()
            _hr = _.find("b", string=re.compile(r"Member Services and Travel"))
            hours = []
            if _hr:
                hours = list(_hr.find_parent().find_next_sibling().stripped_strings)
            yield SgRecord(
                page_url=base_url,
                location_name=_.h2.text.strip(),
                street_address=" ".join(addr[:-2])
                .replace("Corbett Centre", "")
                .strip(),
                city=addr[-2].split(",")[0].strip(),
                state=addr[-2].split(",")[1].strip(),
                zip_postal=addr[-1],
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr).replace("Corbett Centre", "").strip(),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
