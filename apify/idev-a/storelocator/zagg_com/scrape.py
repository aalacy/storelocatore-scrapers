from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("zagg")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.zagg.com"
base_url = "https://www.zagg.com/en_us/amlocator/index/ajax/?p={}&lat=0&lng=0&radius=0&product=0&category=0&sortByDistance=false"

ids = []


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            locations = session.get(base_url.format(page), headers=_headers).json()
            if locations["items"] and locations["items"][0]["id"] in ids:
                break
            logger.info(f"[page {page}] {len(locations['items'])} found")
            page += 1

            for _ in locations["items"]:
                ids.append(_["id"])
                hours = []
                if _["schedule_string"]:
                    for day, hh in json.loads(_["schedule_string"]).items():
                        hours.append(
                            f"{day}: {hh['from']['hours']}:{hh['from']['minutes']}-{hh['to']['hours']}:{hh['to']['minutes']}"
                        )
                _ss = bs(_["popup_html"], "lxml").find(
                    "strong", string=re.compile(r"State")
                )
                state = ""
                if _ss:
                    state = _ss.next.next.strip()
                country_code = _["country"]
                if not country_code and len(_["zip"]) > 5:
                    country_code = "CA"
                yield SgRecord(
                    page_url=f"https://www.zagg.com/en_us/store-finder/{_['url_key']}",
                    location_name=_["name"],
                    store_number=_["id"],
                    street_address=_["address"],
                    city=_["city"],
                    state=state,
                    zip_postal=_["zip"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code=country_code,
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
