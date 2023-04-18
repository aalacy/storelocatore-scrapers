from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("shurgard")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.shurgard.com"
base_url = "https://www.shurgard.com/"


def fetch_data():
    with SgRequests() as session:
        links = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div#top div.hero-image p a"
        )
        codes = []
        for link in links[::-1]:
            code = link["href"].split("/")[-1]
            if "-" not in code:
                continue
            if codes and codes[-1].split("-")[-1] == code.split("-")[-1]:
                continue
            codes.append(code)
        logger.info(f"{len(codes)} found")
        for code in codes:
            url = f"https://www.shurgard.com/{code}/api/stores"
            locations = session.get(url, headers=_headers).json()["stores"]
            for _ in locations:
                page_url = locator_domain + _["url"]
                logger.info(page_url)
                sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                phone = ""
                if sp1.select_one('div[itemprop="telephone"]'):
                    phone = sp1.select_one('div[itemprop="telephone"]').text.strip()
                hours = []
                if sp1.select("ul.hours-table"):
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in sp1.select("ul.hours-table")[0].select("li")
                    ]
                raw_address = " ".join(
                    sp1.select_one("div.store-address").stripped_strings
                )
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=_["address_street"],
                    city=_["city"],
                    zip_postal=_["address_postal"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=code.split("-")[-1],
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
