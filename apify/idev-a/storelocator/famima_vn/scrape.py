from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.famima.vn"
base_url = "http://www.famima.vn/cua-hang/mien-nam/?category=6&zoom=15&is_mile=0&directory_radius=1&view=list&hide_searchbox=1&hide_nav=0&hide_nav_views=0&hide_pager=0&featured_only=0&feature=1&perpage=500&_category=6&sort=newest"


def _d(res, session):
    locations = json.loads(
        res.split("'#sabai-embed-wordpress-shortcode-1 .sabai-directory-map',")[1]
        .split("null,")[0]
        .strip()[:-1]
    )
    for _ in locations:
        info = bs(_["content"], "lxml")
        page_url = info.a["href"]
        logger.info(page_url)
        sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
        raw_address = sp1.select_one('span[itemprop="streetAddress"]').text.strip()
        addr = parse_address_intl(raw_address + ", Vietnam")
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        if street_address.isdigit():
            street_address = raw_address.split(",")[0]
        yield SgRecord(
            page_url=page_url,
            location_name=info.a.text.strip(),
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="VN",
            phone=sp1.select_one("div.sabai-directory-contact").text.strip(),
            locator_domain=locator_domain,
            raw_address=raw_address,
        )


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        for rec in _d(res, session):
            yield rec


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
