from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import dirtyjson as json
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("carrefour")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefour.fr"
base_url = "https://www.carrefour.fr/magasin/"


def fetch_data():
    with SgRequests() as session:
        regions = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "li.store-locator-footer-list__item a"
        )
        for region in regions:
            url = locator_domain + region["href"]
            locations = json.loads(
                session.get(url, headers=_headers)
                .text.split(":context-stores=")[1]
                .split(":context-filters")[0]
                .replace("&quot;", '"')
                .strip()[1:-1]
            )
            for _ in locations:
                addr = _["address"]
                street_address = addr["address1"]
                if addr["address2"]:
                    street_address += " " + addr["address2"]
                hours = []
                try:
                    for day, hh in (
                        _.get("openingWeekPattern", {}).get("timeRanges", {}).items()
                    ):
                        start = hh["begTime"]["date"].split()[-1].split(".")[0]
                        end = hh["endTime"]["date"].split()[-1].split(".")[0]
                        hours.append(f"{day}: {start} - {end}")
                except:
                    pass

                page_url = locator_domain + _["storePageUrl"]
                phone = ""
                location_name = _["name"].replace("&#039;", "'")
                if page_url != base_url:
                    logger.info(page_url)
                    res = session.get(page_url, headers=_headers)
                    if res.status_code == 200:
                        sp1 = bs(res.text, "lxml")
                        location_name = sp1.select_one(
                            "h1.store-page__banner__heading"
                        ).text.strip()
                        location_type = json.loads(
                            sp1.find(
                                "script", string=re.compile(r"tc_vars = Object.assign")
                            )
                            .string.split("tc_vars = Object.assign(tc_vars,")[1]
                            .strip()[:-2]
                        )["store_format"]
                        if sp1.select_one("div.store-meta--telephone a"):
                            phone = sp1.select_one(
                                "div.store-meta--telephone a"
                            ).text.strip()
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=location_name,
                    street_address=street_address.replace("&#039;", "'"),
                    city=addr["city"].replace("&#039;", "'"),
                    state=addr["region"],
                    zip_postal=addr["postalCode"],
                    latitude=addr["geoCoordinates"]["latitude"],
                    longitude=addr["geoCoordinates"]["longitude"],
                    country_code="FR",
                    phone=phone,
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
