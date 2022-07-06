from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl
import ssl
import os

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"

ssl._create_default_https_context = ssl._create_unverified_context


logger = SgLogSetup().get_logger("specsavers")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.specsavers.nl"
base_url = "https://www.specsavers.nl/winkelzoeker/winkeloverzicht"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        cookies = []
        for cookie in driver.get_cookies():
            cookies.append(f"{cookie['name']}={cookie['value']}")
        _headers["cookie"] = "; ".join(cookies)
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("div.item-list ul a")
        for link in locations:
            with SgRequests(proxy_country="us") as session:
                page_url = "https://www.specsavers.nl/winkelzoeker/" + link["href"]
                logger.info(page_url)
                res = session.get(page_url, headers=_headers).text
                sp1 = bs(res, "lxml")
                if (
                    sp1.select_one("h1#page-title")
                    and "Zoek een winkel" in sp1.select_one("h1#page-title").text
                ):
                    continue
                if sp1.select_one("div.store p"):
                    _addr = list(sp1.select_one("div.store p").stripped_strings)
                else:
                    _addr = list(
                        sp1.select_one(
                            "div.field-name-field-store-address"
                        ).stripped_strings
                    )
                try:
                    coord = json.loads(
                        res.split("var position =")[1].split(";")[0].strip()
                    )
                except:
                    coord = {"lat": "", "lng": ""}

                raw_address = (
                    ", ".join(_addr).replace("\n", "").replace("Z.O.", "").strip()
                )
                addr = parse_address_intl(raw_address + ", Netherlands")
                if sp1.select("div.field-name-field-opening-times span.oh-display"):
                    hours = [
                        " ".join(hh.stripped_strings)
                        for hh in sp1.select(
                            "div.field-name-field-opening-times span.oh-display"
                        )
                    ]
                else:
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in sp1.select("table.opening--day-and-time tr")
                    ]
                phone = ""
                if sp1.select_one("a.contact--store-telephone"):
                    phone = sp1.select_one("a.contact--store-telephone").text.strip()

                location_type = (
                    link.find_parent("div")
                    .find_parent()
                    .find_previous_sibling()
                    .text.strip()
                )
                yield SgRecord(
                    page_url=page_url,
                    location_name=sp1.h1.text.strip(),
                    street_address=_addr[0].replace("\n", "").replace(",", " ").strip(),
                    city=addr.city or sp1.h1.text.strip(),
                    zip_postal=_addr[-2],
                    country_code="Netherlands",
                    phone=phone,
                    latitude=coord["lat"],
                    longitude=coord["lng"],
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
