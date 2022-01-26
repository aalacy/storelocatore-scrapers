from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("cleanslatecenters")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _h(temp):
    hours = []
    for hh in temp:
        if "call" in hh.lower() or "hour" in hh.lower():
            break
        hours.append(
            hh.split("(")[0]
            .strip()
            .replace("–", "-")
            .replace("\xa0", "")
            .replace("    ", " ")
        )

    return hours


def fetch_data():
    locator_domain = "https://www.cleanslatecenters.com/"
    base_url = "https://www.cleanslatecenters.com/our-location"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("h4.et_pb_module_header a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            raw_address = list(
                sp1.find("h4", string=re.compile(r"^ADDRESS$"))
                .find_next_sibling("p")
                .stripped_strings
            )
            addr = parse_address_intl(" ".join(raw_address))
            state = addr.state
            if not state:
                state = link.text.split(",")[-1]
            _hr = sp1.find("h4", string=re.compile(r"HOURS OF OPERATION"))
            hours = []
            if _hr:
                if _hr.find_next_sibling("p"):
                    hours = list(_hr.find_next_sibling("p").stripped_strings)
                elif _hr.find_next_sibling("div") and _hr.find_next_sibling("div").p:
                    hours = list(_hr.find_next_sibling("div").p.stripped_strings)

            else:
                _hr = sp1.find("strong", string=re.compile(r"HOURS OF OPERATION"))
                if _hr:
                    hours = list(_hr.find_parent().find_next_sibling().stripped_strings)

            try:
                coord = (
                    sp1.iframe["data-src"]
                    .split("!2d")[1]
                    .split("!3m")[0]
                    .split("!2m")[0]
                    .split("!3d")
                )
            except:
                coord = ["", ""]
            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=" ".join(raw_address[:-1]),
                city=addr.city,
                state=state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=sp1.find("a", href=re.compile(r"tel:")).text.strip(),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(_h(hours)).replace("\xa0", ""),
                raw_address=" ".join(raw_address),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
