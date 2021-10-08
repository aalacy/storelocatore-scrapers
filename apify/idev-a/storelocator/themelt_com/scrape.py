from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def _p(val):
    if (
        val.replace("(", "")
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
    locator_domain = "https://www.themelt.com/"
    base_url = "https://www.themelt.com/locations"
    json_url = "/_api/wix-code-public-dispatcher/siteview/wix/data-web.jsw"
    with SgChrome() as driver:
        driver.get(base_url)
        driver.wait_for_request(json_url, 20)
        for rr in driver.iter_requests():
            if json_url in rr.url:
                locations = json.loads(rr.response.body)
                
                for _ in locations["result"]["items"]:
                    hours = []
                    if _["days_01"]:
                        hours.append(f"{_['days_01']}: {_['hours_01']}")
                    if _.get("days_02", "").strip():
                        hours.append(f"{_['days_02']}: {_['hours_02']}")
                    if _.get("days_03", "").strip():
                        hours.append(f"{_['days_03']}: {_['hours_03']}")
                    street_address = _["address"]
                    cross_street = _["cross_streets"].split("\n")[-1]
                    if "St." not in street_address and "St." in cross_street:
                        street_address = cross_street
                    if cross_street.split(" ")[0].strip().isdigit():
                        street_address = cross_street
                    yield SgRecord(
                        page_url=base_url,
                        location_name=_["address"],
                        street_address=street_address,
                        city=_["city"],
                        state=_["state"],
                        country_code="US",
                        phone=_p(_["phone_number"]),
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
