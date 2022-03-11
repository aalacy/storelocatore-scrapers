from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re

logger = SgLogSetup().get_logger("mondou")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.mondou.com"
base_url = (
    "https://www.mondou.com/fr-CA/stores?showMap=true&horizontalView=true&isForm=true"
)


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
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml").select_one(
                "div.map-canvas"
            )["data-locations"]
        )
        for _ in locations:
            info = bs(_["infoWindowHtml"], "lxml")
            page_url = (
                locator_domain + info.select_one("div.store-see-details a")["href"]
            )
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            if "Ouverture le" in sp1.select_one("h5.col-12").text:
                continue
            addr = list(sp1.select_one("div.store-address a").stripped_strings)
            hours = []
            _hr = sp1.find("h5", string=re.compile(r"^Horaire"))
            if _hr:
                temp = list(_hr.find_next_sibling().stripped_strings)
                for x in range(0, len(temp), 2):
                    hours.append(f"{temp[x]}: {temp[x+1]}")
            s_z = addr[-1].split(",")[1].strip().split()
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=s_z[0],
                zip_postal=" ".join(s_z[1:]),
                country_code="CA",
                phone=_p(sp1.select("div.store-address a")[1].text),
                locator_domain=locator_domain,
                latitude=_["latitude"],
                longitude=_["longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
