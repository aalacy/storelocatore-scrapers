from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("taxassist")


_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}
locator_domain = "https://www.taxassist.co.uk/"
base_url = "https://www.taxassist.co.uk/locations"


def _fix(original):
    regex = re.compile(r'\\(?![/u"])')
    return regex.sub(r"\\\\", original).replace("\t", "").replace("\n", "")


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    soup = bs(http.get(base_url, headers=_headers).text, "lxml")
    links = [link["href"] for link in soup.select("main div.row a.primary.outline")]
    logger.info(f"{len(links)} found")
    for page_url in links:
        sp1 = bs(http.get(page_url, headers=_headers).text, "lxml")
        details = [dd["href"] for dd in sp1.select("main div.mt-auto a.outline")]
        if details:
            for url in details:
                state.push_request(SerializableRequest(url=url))
        else:
            state.push_request(SerializableRequest(url=page_url))

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        page_url = next_r.url
        logger.info(page_url)
        res = http.get(page_url)
        if res.status_code != 200:
            continue
        sp2 = bs(res.text, "lxml")
        location = json.loads(
            _fix(sp2.find("script", type="application/ld+json").string.strip())
        )
        if location["address"]["streetAddress"] == "Coming Soon":
            continue
        hours = []
        for _ in location["openingHoursSpecification"]:
            hour = f"{_['opens']}-{_['closes']}"
            if hour == "00:00-00:00":
                hour = "closed"
            hours.append(f"{_['dayOfWeek']}: {hour}")
        hours_of_operation = "; ".join(hours)
        if re.search(r"please contact", hours_of_operation, re.IGNORECASE):
            hours_of_operation = ""
        yield SgRecord(
            page_url=page_url,
            location_type=location["@type"],
            location_name=location["name"],
            street_address=location["address"]["streetAddress"],
            city=location["address"]["addressLocality"],
            zip_postal=location["address"]["postalCode"],
            country_code="uk",
            latitude=location["geo"]["latitude"],
            longitude=location["geo"]["longitude"],
            phone=location["telephone"],
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
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
