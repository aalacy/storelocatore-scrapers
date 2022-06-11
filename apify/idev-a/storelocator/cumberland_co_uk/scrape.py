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

locator_domain = "https://www.cumberland.co.uk"
base_url = "https://www.cumberland.co.uk/about/branch-finder"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("li.m-Map-sidebarListItem")
        for _ in locations:
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            raw_address = " ".join(
                sp1.select_one('div[itemprop="address"]').stripped_strings
            )
            coord = _["data-latlng"].split(",")
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("table.Table--plain tr")
            ]
            location_type = ""
            if sp1.select_one("div.pill--error"):
                error = sp1.select_one("div.pill--error").text
                if "Closed for refurbishment" in error or "Temporarily closed" in error:
                    location_type = "Temporarily closed"
            yield SgRecord(
                page_url=page_url,
                location_name=_.select_one("div.m-Map-sidebarListHeading").text.strip(),
                street_address=sp1.select_one(
                    'span[itemprop="streetAddress"]'
                ).text.strip(),
                city=sp1.select_one('span[itemprop="addressLocality"]').text.strip(),
                zip_postal=sp1.select_one('span[itemprop="postalCode"]').text.strip(),
                country_code="UK",
                phone=sp1.select_one('div[itemprop="telephone"] a').text.strip(),
                latitude=coord[0],
                longitude=coord[1],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
