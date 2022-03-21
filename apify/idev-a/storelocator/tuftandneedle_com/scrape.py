from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import ssl
import time
import json


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("tuftandneedle")

locator_domain = "https://www.tuftandneedle.com"
base_url = "https://www.tuftandneedle.com/stores/all/"
json_url = "https://ipa.tuftandneedle.com/api/graphql"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests:
                logger.info(rr.url)
                if (
                    rr.url == json_url
                    and rr.response
                    and json.loads(rr.response.body)
                    .get("data", {})
                    .get("getStores", {})
                ):
                    exist = True
                    locations = json.loads(rr.response.body)["data"]["getStores"][
                        "results"
                    ]["retailStores"]
                    for _ in locations:
                        if _["comingSoon"]:
                            continue
                        street_address = _["address"]["line1"]
                        if _["address"]["line2"]:
                            street_address += " " + _["address"]["line2"]
                        page_url = f"https://www.tuftandneedle.com/stores/retail-stores/{_['uuid']}"
                        yield SgRecord(
                            page_url=page_url,
                            location_name=_["name"],
                            street_address=street_address,
                            city=_["address"]["city"],
                            state=_["address"]["state"],
                            zip_postal=_["address"]["zip"],
                            latitude=_["lat"],
                            longitude=_["lng"],
                            country_code="US",
                            phone=_["phoneNumber"],
                            locator_domain=locator_domain,
                            hours_of_operation="; ".join(_["hours"]),
                        )
                    break


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
