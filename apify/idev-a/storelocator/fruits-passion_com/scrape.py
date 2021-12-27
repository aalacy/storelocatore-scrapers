from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("mycarecompass")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://fruits-passion.com"
base_url = "https://fruits-passion.com/en-ca/amlocator/"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def _coord(block, _):
    latitude = longitude = ""
    for loc in block["items"]:
        if str(loc["id"]) == _["data-amid"]:
            latitude = loc["lat"]
            longitude = loc["lng"]
            break
    return latitude, longitude


def fetch_data():
    with SgRequests() as session:
        block = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("jsonLocations:")[1]
            .split("imageLocations:")[0]
            .strip()[:-1]
        )
        for _ in bs(block["block"], "lxml").select("div.amlocator-store-desc"):
            latitude, longitude = _coord(block, _)
            addr = list(
                _.select_one("div.amlocator-store-information").stripped_strings
            )[-5:]
            if "Distance" in addr[-1]:
                del addr[-1]
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in _.select("div.amlocator-week div.amlocator-row")
            ]
            location_type = ""
            if "Temporarily closed" in _.select_one("div.amlocator-description").text:
                location_type = "Temporarily closed"
            page_url = _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            phone = ""
            if sp1.select_one("span.amlocator-icon.-phone"):
                phone = (
                    sp1.select_one("span.amlocator-icon.-phone")
                    .find_next_sibling()
                    .text.strip()
                )
            yield SgRecord(
                page_url=page_url,
                location_name=_.select_one("div.amlocator-title").text.strip(),
                street_address=addr[0],
                city=addr[1],
                state=addr[2].split(",")[0].strip(),
                zip_postal=addr[-1],
                latitude=latitude,
                longitude=longitude,
                country_code="CA",
                location_type=location_type,
                locator_domain=locator_domain,
                phone=phone,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
