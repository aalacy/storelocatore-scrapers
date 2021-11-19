from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("schoolofrock")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.schoolofrock.com"
base_url = "https://locations.schoolofrock.com/"


def fetch_records(http):
    locs = json.loads(
        http.get(base_url, headers=_headers)
        .text.split("var closestLocations =")[1]
        .split("</script>")[0]
        .strip()[:-1]
    )
    for _ in locs:
        page_url = _["url"]
        logger.info(page_url)
        sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
        bar = sp1.select_one("div.promo-bar")
        if (
            bar
            and "coming soon" in bar.text.lower()
            and "black friday" not in bar.text.lower()
            and "summer camp" not in bar.text.lower()
        ):
            continue
        hours = [
            hh.text.replace("\n", "").replace("   ", "").strip()
            for hh in sp1.select("ul.open-hours li")
        ]
        yield SgRecord(
            page_url=page_url,
            store_number=_["id"],
            location_name=_["name"],
            street_address=_["address"],
            city=_["city"],
            state=_.get("state"),
            zip_postal=_.get("zip"),
            country_code=_["country"],
            latitude=_["display_latitude"],
            longitude=_["display_longitude"],
            phone=_.get("phone"),
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http):
                writer.write_row(rec)
