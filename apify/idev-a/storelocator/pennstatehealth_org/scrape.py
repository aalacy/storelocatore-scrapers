from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgselenium import SgChrome
import time
import json
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("mycarecompass")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.pennstatehealth.org"
    base_url = "https://www.pennstatehealth.org/locations/results"
    json_url = "https://www.pennstatehealth.org/locations/results?ajax_form=1&_wrapper_format=drupal_ajax"
    with SgRequests() as session:
        with SgChrome() as driver:
            driver.get(base_url)
            exist = False
            while not exist:
                time.sleep(1)
                for rr in driver.requests:
                    if rr.url == json_url and rr.response:
                        exist = True
                        coms = json.loads(rr.response.body)
                        for cc in coms:
                            if (
                                cc["command"] == "insert"
                                and cc["selector"] == ".results"
                                and cc["method"] == "html"
                            ):
                                locations = bs(cc["data"], "lxml").select("article")
                                logger.info(f"{len(locations)} found")
                                for _ in locations:
                                    street_address = _.select_one(
                                        "span.address-line1"
                                    ).text.strip()
                                    if _.select_one("span.address-line2"):
                                        street_address += (
                                            " "
                                            + _.select_one(
                                                "span.address-line2"
                                            ).text.strip()
                                        )
                                    page_url = (
                                        locator_domain
                                        + _.find("a", href=re.compile(r"/locations"))[
                                            "href"
                                        ]
                                    )
                                    sp1 = bs(
                                        session.get(page_url, headers=_headers).text,
                                        "lxml",
                                    )
                                    logger.info(page_url)
                                    script = json.loads(
                                        sp1.find(
                                            "script", type="application/ld+json"
                                        ).string
                                    )
                                    location_type = []
                                    if "imaging" in _.h3.text.lower():
                                        location_type.append("imaging")
                                    if "Lab" in _.h3.text:
                                        location_type.append("lab")
                                    if "urgent care" in _.h3.text.lower():
                                        location_type.append("urgent care")
                                    if (
                                        "medical center" in _.h3.text.lower()
                                        or "hospital" in _.h3.text.lower()
                                    ):
                                        location_type.append("hospital")
                                    if not location_type:
                                        location_type = ["medical group"]

                                    yield SgRecord(
                                        page_url=page_url,
                                        store_number=_["location_id"],
                                        location_name=_.h3.text.split("-")[0]
                                        .split("–")[0]
                                        .strip(),
                                        street_address=street_address,
                                        city=_.select_one("span.locality").text.strip(),
                                        state=_.select_one(
                                            "span.administrative-area"
                                        ).text.strip(),
                                        zip_postal=_.select_one(
                                            "span.postal-code"
                                        ).text.strip(),
                                        latitude=script["geo"]["latitude"],
                                        longitude=script["geo"]["longitude"],
                                        country_code="US",
                                        location_type=", ".join(location_type),
                                        phone=script.get("telephone"),
                                        locator_domain=locator_domain,
                                        hours_of_operation=script.get("openingHours"),
                                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
