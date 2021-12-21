from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

logger = SgLogSetup().get_logger("royalbank")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.royalbank-usa.com"
base_url = "https://www.royalbank-usa.com/locations.asp"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.column.content div.row")
        logger.info(f"{len(links)} found")
        for link in links:
            addr = list(link.p.stripped_strings)
            _hr = link.find("strong", string=re.compile(r"Lobby Hours"))
            hours = []
            if not _hr:
                _hr = link.find("strong", string=re.compile(r"Office Hours"))
            if _hr:
                hours = list(_hr.find_parent("p").stripped_strings)[1:]

            city = addr[-1].split(",")[0].strip()
            phone = ""
            if link.find("a", href=re.compile(r"tel:")):
                phone = (
                    link.find("a", href=re.compile(r"tel:")).text.split(":")[-1].strip()
                )
            yield SgRecord(
                page_url=base_url,
                location_name=city,
                street_address=addr[0],
                city=city,
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("\x80\x93", "-")
                .replace("â", ""),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
