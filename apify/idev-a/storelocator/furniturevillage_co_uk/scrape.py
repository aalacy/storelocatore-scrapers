from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
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

logger = SgLogSetup().get_logger("furniturevillage")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.furniturevillage.co.uk"
base_url = "https://www.furniturevillage.co.uk/stores/"


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            links = soup.find(
                "div", {"class": "col-xs-12 select-store no-pd"}
            ).find_all("option")
            logger.info(f"{len(links)} found")
            for link in links:
                if not link["value"]:
                    continue
                page_url = locator_domain + link["value"]
                logger.info(page_url)
                driver.get(page_url)
                soup1 = bs(driver.page_source, "lxml")
                addr = list(soup1.select_one('p[itemprop="address"]').stripped_strings)
                raw_address = " ".join(addr)
                street_address = ""
                city = soup1.find("span", {"itemprop": "addressLocality"}).text.strip()
                for x, aa in enumerate(addr):
                    if aa == city:
                        street_address = " ".join(addr[:x])

                state = soup1.find("span", {"itemprop": "addressRegion"}).text.strip()
                zipp = soup1.find("span", {"itemprop": "postalCode"}).text.strip()
                phone = soup1.find("meta", {"itemprop": "telephone"})["content"]
                latitude = soup1.find("meta", {"itemprop": "latitude"})["content"]
                longitude = soup1.find("meta", {"itemprop": "longitude"})["content"]
                hours = []
                location_type = ""
                for hour in soup1.select("div.item-hours p"):
                    if re.search(r"This store reopens on", hour.text, re.IGNORECASE):
                        location_type = "Closed"
                        break
                    if re.search(r"temporarily closed", hour.text, re.IGNORECASE):
                        location_type = "temporarily Closed"
                        break
                    if re.search(r"re open", hour.text, re.IGNORECASE):
                        continue
                    if "Boxing" in hour.text or "New" in hour.text:
                        continue
                    hours.append(": ".join(hour.stripped_strings))

                yield SgRecord(
                    page_url=page_url,
                    location_name=link.text.strip(),
                    street_address=street_address,
                    city=city,
                    state=state,
                    latitude=latitude,
                    longitude=longitude,
                    zip_postal=zipp,
                    country_code="Uk",
                    phone=phone,
                    locator_domain=locator_domain,
                    location_type=location_type,
                    hours_of_operation="; ".join(hours).split(": (")[0].strip(),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
