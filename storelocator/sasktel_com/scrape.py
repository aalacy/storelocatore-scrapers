from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("sasktel")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.sasktel.com/"
base_url = "https://www.sasktel.com/dealers/"
json_url = "https://www.sasktel.com/findadealer?lat=50.455&lng=-104.609&searchtype=location&sortby=distance&limit=2000&sortorder=asc&distance=5000&type=SKST&type=SKDL"


def _v(val):
    if (
        val.startswith("Unit")
        or val.startswith("#")
        or val.split("-")[0].strip().isdigit()
        or val.split(" ")[0].strip().isdigit()
    ):
        return val.strip()
    else:
        return (
            val.split("-")[-1]
            .split("Mall")[-1]
            .split("Plaza")[-1]
            .split("Landing")[-1]
            .replace("Grasslands", "")
            .split("Gate")[-1]
            .replace("&#39;", "'")
            .replace("&amp;", "&")
            .replace("Box", "")
            .split("Floor")[-1]
            .strip()
        )


def fetch_data():
    with SgRequests() as session:
        locations = session.get(json_url, headers=_headers).json()["data"]
        for _ in locations:
            street_address = _["address"]["line1"]
            if _["address"]["line2"]:
                street_address += " " + _["address"]["line2"]
            phone = ""
            if _["contacts"]["tel"]:
                phone = _["contacts"]["tel"][0]
            hours = []
            for hh in bs(_["hours"], "lxml").stripped_strings:
                if "Hours" in hh or "Book" in hh:
                    continue
                hours.append(hh)
            yield SgRecord(
                page_url=base_url,
                location_name=_["name"].replace("&#39;", "'").replace("&amp;", "&"),
                street_address=_v(street_address),
                city=_["address"]["city"].replace("&#39;", "'").replace("&amp;", "&"),
                zip_postal=_["address"]["postalCode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="CA",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
