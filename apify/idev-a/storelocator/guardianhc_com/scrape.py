from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("guardianhc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://guardianhc.com"
base_url = "https://guardianhc.com/locations"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var maplistScriptParamsKo =")[1]
            .split("/* ]]> */")[0]
            .strip()[:-1]
        )["KOObject"][0]["locations"]
        for _ in locations:
            addr = list(
                bs(_["description"], "lxml").select_one("div.address").stripped_strings
            )
            phone = ""
            simple = list(bs(_["simpledescription"], "lxml").stripped_strings)
            if simple and "Phone" in simple[0]:
                phone = simple[1]
            yield SgRecord(
                page_url=_["locationUrl"],
                store_number=_["cssClass"].strip().split()[-1].split("-")[-1],
                location_name=_["title"],
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=phone,
                location_type=_["cssClass"].strip().split()[0],
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
