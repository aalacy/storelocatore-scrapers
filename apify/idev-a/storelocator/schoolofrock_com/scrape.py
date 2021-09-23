from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("schoolofrock")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.schoolofrock.com"
base_url = "https://locations.schoolofrock.com/"


def record_initial_requests(http, state):
    locs = json.loads(
        http.get(base_url, headers=_headers)
        .text.split("var closestLocations =")[1]
        .split("</script>")[0]
        .strip()[:-1]
    )
    for loc in locs:
        url = loc["url"]
        state.push_request(SerializableRequest(url=url, context={"loc": loc}))

    return True


def fetch_records(http, state):
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)

        sp1 = bs(http.get(next_r.url, headers=_headers).text, "lxml")
        hours = [
            hh.text.replace("\n", "").replace("   ", "").strip()
            for hh in sp1.select("ul.open-hours li")
        ]
        _ = next_r.context.get("loc")
        yield SgRecord(
            page_url=next_r.url,
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
    state = CrawlStateSingleton.get_instance()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)
