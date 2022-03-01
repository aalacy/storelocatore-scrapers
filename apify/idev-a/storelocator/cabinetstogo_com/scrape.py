from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import demjson
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://cabinetstogo.com"
base_url = "https://cabinetstogo.com/pages/showrooms"


def fetch_data():
    with SgRequests() as session:
        json_url = (
            "https:"
            + bs(session.get(base_url, headers=_headers).text, "lxml").find(
                "script", src=re.compile(r"/assets/showroomsDatabase.js")
            )["src"]
        )
        locations = demjson.decode(
            session.get(json_url, headers=_headers)
            .text.split("var stores=")[1]
            .split("//#")[0]
            .strip()[:-1]
        )
        for _ in locations:
            if "COMING SOON" in _["showroom"]:
                continue
            if "RELOCATED" in _["showroom"]:
                continue
            hours = list(bs(_["hours"], "lxml").stripped_strings)
            if "Please contact store" in hours[0]:
                del hours[0]
            if "Due to" in hours[0]:
                del hours[0]

            phone = _["phone"]
            if "not available" in phone:
                phone = ""
            hours_of_operation = "; ".join(hours)
            if (
                "not available" in hours_of_operation
                or "RELOCATED" in hours_of_operation
            ):
                hours_of_operation = ""
            yield SgRecord(
                page_url=locator_domain + _["storelink"],
                location_name=_["showroom"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                latitude=_["lat"],
                longitude=_["lon"],
                phone=phone,
                zip_postal=_["zip"],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
