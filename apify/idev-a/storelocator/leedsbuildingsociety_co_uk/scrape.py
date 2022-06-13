from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("uk")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.leedsbuildingsociety.co.uk"
base_url = "https://www.leedsbuildingsociety.co.uk/find-a-branch/branches/"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("div#main-content div.main-article ul li a")
        for link in locations:
            page_url = base_url + link["href"]
            logger.info(page_url)
            driver.get(page_url)
            sp1 = bs(driver.page_source, "lxml")
            raw_address = (
                sp1.select_one('p[itemprop="address"]').text.replace("\n", "").strip()
            )
            for script in sp1.find_all("script"):
                res = script.text
                try:
                    latitude = res.split("var myLat =")[1].split("var")[0].strip()[1:-2]
                    longitude = (
                        res.split("var myLng =")[1].split("var")[0].strip()[1:-2]
                    )
                    break
                except:
                    pass
            hours = []
            for hh in sp1.select("p.ux_details-openingHours-body_p"):
                if "Holiday" in hh.text:
                    break
                hours.append(": ".join(hh.stripped_strings))
            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=sp1.select_one('span[itemprop="streetAddress"]')
                .text.replace("\n", "")
                .replace(",", " ")
                .strip(),
                city=sp1.select_one('span[itemprop="addressLocality"]')
                .text.replace("\n", "")
                .replace(",", " ")
                .strip(),
                zip_postal=sp1.select_one('span[itemprop="postalCode"]').text.strip(),
                country_code="UK",
                phone=sp1.select_one('span[itemprop="telephone"]').text.strip(),
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                raw_address=raw_address,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
