from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


logger = SgLogSetup().get_logger("toms.com")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.toms.com"
base_url = "https://www.toms.com/us/toms-stores.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.experience-commerce_assets-contentTile")
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.select_one("span.c-content-tile__box-title"):
                continue
            hours = []
            _hr = link.find("strong", string=re.compile(r"Store hours", re.IGNORECASE))
            if _hr:
                for hh in _hr.find_parent().find_next_siblings("p"):
                    if not hh.text.strip() or "hour" in hh.text.lower():
                        break
                    hours.append(hh.text.strip())

            _addr = []
            for aa in (
                link.find("strong", string=re.compile(r"Location"))
                .find_parent()
                .find_next_siblings("p")
            ):
                if "Phone" in aa.text:
                    break
                if not aa.text.strip():
                    continue
                _addr.append(aa.text)

            if not _addr[0][0].isdigit():
                del _addr[0]
            phone = ""
            pp = link.find("", string=re.compile(r"Phone"))
            if pp and pp.find_parent("strong"):
                phone = pp.find_parent("p").text.replace("Phone", "")
                if not phone:
                    phone = (
                        link.find("strong", string=re.compile(r"Phone"))
                        .find_parent()
                        .find_next_sibling("p")
                        .text.strip()
                    )
            yield SgRecord(
                page_url=base_url,
                location_name=link.select_one("span.c-content-tile__box-title")
                .text.replace("Store Details", "")
                .strip(),
                street_address=" ".join(_addr[:-1]),
                city=_addr[-1].split(",")[0].strip(),
                state=_addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=_addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=", ".join(_addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
