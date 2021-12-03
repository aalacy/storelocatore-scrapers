from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.famima.vn"
base_url = "https://www.famima.vn/en/sabai/directory?p=1&category=0&zoom=15&is_mile=0&directory_radius=1&view=list&hide_searchbox=1&hide_nav=1&hide_nav_views=0&hide_pager=0&featured_only=0&feature=1&perpage=500&sort=newest&__ajax=%23sabai-embed-wordpress-shortcode-1%20.sabai-directory-listings-container&_=1638268677724"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.sabai-directory-main a")
        for loc in locations:
            page_url = loc["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            yield SgRecord(
                page_url=page_url,
                location_name=loc.text.strip(),
                street_address=sp1.select_one(
                    'span[itemprop="streetAddress"]'
                ).text.strip(),
                city=sp1.select_one('span[itemprop="addressRegion"]').text.strip(),
                country_code="VN",
                phone=sp1.select_one("div.sabai-directory-contact").text.strip(),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
