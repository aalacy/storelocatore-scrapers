from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

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
            res.split("var GTU_L_Locations =")[1].split("/* ]]> */")[0].strip()[:-1]
        )
        for _ in locations:
            if not _["ACF"]["street"]:
                continue
            if _["ACF"].get("coming_soon") == "yes":
                continue
            if (_["ACF"].get("country") or "US") not in ["US", "CA"]:
                logger.info(f'[Non US] {_["ACF"].get("country")} - {_["post_name"]}')
                continue
            page_url = f"{locator_domain}{_['post_name']}"
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = [
                ": ".join(hh.stripped_strings) for hh in sp1.select("div#hours div.row")
            ]
            yield SgRecord(
                page_url=page_url,
                store_number=_["ID"],
                location_name=_["post_title"],
                street_address=_["ACF"]["street"],
                city=_["ACF"]["city"],
                state=_["ACF"]["state"],
                latitude=_["ACF"]["latitude"],
                longitude=_["ACF"]["longitude"],
                zip_postal=_["ACF"]["zip"],
                country_code=_["ACF"].get("country", "US") or "US",
                phone=_["ACF"]["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
