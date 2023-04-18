from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.ee"
base_url = "https://mcdonalds.ee/positsioneeri/"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        res = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var wpjs =")[1]
            .split(";")[0]
        )
        data = {"action": "get_locations", "token": res["ajax_nonce"]}
        locations = session.post(res["ajax_url"], headers=_headers, data=data).json()[
            "data"
        ]
        for _ in locations:
            bb = list(bs(_["address"], "lxml").stripped_strings)
            phone = ""
            if _p(bb[-1]):
                phone = bb[-1]
                del bb[-1]
            addr = _["latlng"]
            street_address = addr["street_name"]
            if addr["street_number"]:
                street_address += " " + addr["street_number"]
            page_url = _["permalink"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for hh in sp1.select_one("table.location-hours-table").select("tr"):
                hours.append(": ".join(hh.stripped_strings))
            yield SgRecord(
                page_url=page_url,
                store_number=_["ID"],
                location_name=_["title"],
                street_address=street_address,
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr["post_code"],
                latitude=addr["lat"],
                longitude=addr["lng"],
                country_code=addr["country"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(bb),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
