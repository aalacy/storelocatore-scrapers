from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "Host": "www.a1mri.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

locator_domain = "https://www.a1mri.com"
base_url = "https://www.a1mri.com/locations"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            "div.dmDefaultListContentRow  div.dmRespColsWrapper .dmRespCol"
        )
        for _ in locations:
            if not _.text:
                continue

            page_url = locator_domain + _.a["href"]
            block = list(_.stripped_strings)
            del block[0]
            state_zip = block[1].split(",")[1].strip().split(" ")
            res = session.get(page_url, headers=_headers)
            coord = {}
            if res.status_code == 200:
                soup1 = bs(res.text, "lxml")
                coord = soup1.select_one('div[data-type="inlineMap"]')
            yield SgRecord(
                page_url=page_url,
                location_name=_.a.text,
                street_address=block[0],
                city=block[1].split(",")[0],
                state=state_zip[0],
                zip_postal=state_zip[-1],
                country_code="US",
                phone=soup1.find("a", href=re.compile(r"tel:")).text,
                latitude=coord.get("data-lat"),
                longitude=coord.get("data-lng"),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
