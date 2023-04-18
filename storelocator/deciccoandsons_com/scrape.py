from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("deciccoandsons")

locator_domain = "https://www.deciccoandsons.com"
base_url = "https://www.deciccoandsons.com/locations/"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .replace("’", "'")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.full_width_inner div.grid_section h2 a")
        for link in locations:
            page_url = locator_domain + link["href"]
            logger.info(page_url)
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            visit = soup1.find("h2", string=re.compile(r"visit us", re.IGNORECASE))
            if not visit:
                continue
            addr = list(visit.find_next_sibling("p").stripped_strings)
            coord = (
                soup1.select_one(".wpb_map_wraper iframe")["src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3d")
            )
            phone_block = soup1.find("h2", string=re.compile(r"^phone", re.IGNORECASE))
            phone = phone_block.find_next_sibling("p").text.strip()
            hour_block = soup1.find(
                "h2", string=re.compile(r"^Store Hours", re.IGNORECASE)
            )
            hours = list(hour_block.find_next_sibling("p").stripped_strings)
            yield SgRecord(
                page_url=page_url,
                location_name=link.text,
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                phone=phone,
                latitude=coord[1],
                longitude=coord[0],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
