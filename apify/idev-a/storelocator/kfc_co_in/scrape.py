from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kfc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://online.kfc.co.in/"
base_url = "https://restaurants.kfc.co.in/?page={}"


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            locations = soup.select("div.store-info-box")
            if not locations:
                break
            page += 1
            logger.info(f"[page {page}] {len(locations)} found")
            for _ in locations:
                addr = [
                    aa.text.strip()
                    for aa in _.select_one(".outlet-address .info-text").findChildren(
                        "span", recursive=False
                    )
                ]
                hours = (
                    _.select_one(".outlet-phone").find_next_sibling("li").text.strip()
                )
                yield SgRecord(
                    page_url=_.select_one("a.btn-website")["href"],
                    location_name=_.select_one(".outlet-name").text.strip(),
                    street_address=" ".join(addr[:-1]).replace("\n", " "),
                    city=addr[-1].split("-")[0].strip(),
                    zip_postal=addr[-1].split("-")[-1].strip(),
                    country_code="India",
                    phone=_.select_one(".outlet-phone").text.strip(),
                    latitude=_.select_one("input.outlet-latitude")["value"],
                    longitude=_.select_one("input.outlet-longitude")["value"],
                    locator_domain=locator_domain,
                    hours_of_operation=hours,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
