from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.coventrybuildingsociety.co.uk"
branch_url = "https://www.coventrybuildingsociety.co.uk/member/our-branches.html"
agency_url = (
    "https://www.coventrybuildingsociety.co.uk/member/our-branches/all-agencies.html"
)


def fetch_data():
    with SgRequests() as session:
        # branch
        soup = bs(session.get(branch_url, headers=_headers).text, "lxml")
        locations = soup.find_all("a", href=re.compile(r"/member/our-branches"))
        for link in locations:
            page_url = locator_domain + link["href"]
            if (
                "all-agencies.html" in page_url
                or "our-branches.html" in page_url
                or "branch-refit.html" in page_url
            ):
                continue
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _aa = sp1.find("span", string=re.compile(r"^Branch Details"))
            if not _aa:
                continue
            aa = _aa.find_parent("div").find_parent().find_next_sibling()
            block = list(aa.stripped_strings)
            raw_address = block[0]
            addr = raw_address.split(",")
            phone = ""
            if "Telephone" in block[-1]:
                phone = block[-1].replace("Telephone:", "")

            hr = (
                sp1.find("span", string=re.compile(r"^Current opening hours"))
                .find_parent("div")
                .find_parent()
                .find_next_sibling()
            )
            hours = [
                hh.text.strip()
                for hh in hr.select("p")
                if hh.text.strip() and "hour" not in hh.text
            ]
            zip_postal = " ".join(addr[-1].strip().split()[-2:])
            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=" ".join(addr[:-1]),
                city=link.text.split("-")[0].strip(),
                zip_postal=zip_postal,
                country_code="UK",
                phone=phone,
                location_type="branch",
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours).replace("\n", "; "),
            )

        # agency
        soup = bs(session.get(agency_url, headers=_headers).text, "lxml")
        block1 = soup.select("div.aem-Grid.aem-Grid--default--5.aem-Grid--phone--6")
        block2 = soup.select("div.aem-Grid--default--7.aem-Grid--phone--6 ")
        for x in range(len(block1)):
            info = list(block1[x].stripped_strings)
            com = block2[x].select("div.cbsTextComponent")
            raw_address = com[0].text.strip()
            addr = raw_address.split(",")
            yield SgRecord(
                page_url=agency_url,
                location_name=info[0],
                street_address=" ".join(addr[:-2]),
                city=addr[-2].strip(),
                zip_postal=addr[-1].strip(),
                country_code="UK",
                phone=info[-1],
                location_type="agency",
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(com[-1].stripped_strings),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
