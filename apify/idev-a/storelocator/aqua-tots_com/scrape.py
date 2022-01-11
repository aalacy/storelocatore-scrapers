from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("aqua-tots")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    locator_domain = "https://www.aqua-tots.com/"
    base_url = "https://www.aqua-tots.com/location-finder/"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = json.loads(
            res.split("var wpgmp_gtu_data =")[1].split("/* ]]> */")[0].strip()[:-1]
        )["places"]
        for _ in locations:
            loc = _["location"]
            country_code = loc["extra_fields"]["category_slug"].replace("-", " ")
            page_url = loc["extra_fields"]["sl_url"].replace(
                "awww.aqua-tots.com", "www.aqua-tots.com"
            )
            if country_code and country_code not in ["united states", "canada"]:
                continue
            if "Bangkok" == loc["state"]:
                continue
            logger.info(page_url)
            hours = []
            if page_url:
                res1 = session.get(page_url, headers=_headers)
                if res1.status_code == 200:
                    sp1 = bs(res1.text, "lxml")
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in sp1.select("div#hours div.row")
                    ]

            is_coming_soon = False
            for cat in _["categories"]:
                if cat["name"] == "Coming Soon":
                    is_coming_soon = True
                    break

            if is_coming_soon:
                continue

            yield SgRecord(
                page_url=page_url or base_url,
                store_number=_["id"],
                location_name=_["title"],
                street_address=_["address"],
                city=loc["city"],
                state=loc["state"],
                latitude=loc["lat"],
                longitude=loc["lng"],
                zip_postal=loc["postal_code"],
                country_code=country_code,
                phone=loc["extra_fields"]["sl_phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
