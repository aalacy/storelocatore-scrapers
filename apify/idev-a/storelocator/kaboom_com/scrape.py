from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import ssl
import dirtyjson as json

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("kaboom")

locator_domain = "http://www.kaboom.com/"
base_url = "https://www.kaboom.com/locations"
json_url = "https://www.kaboom.com/app/website/cms/api/v1/pages/"


def _p(val):
    if (
        val
        and val.replace("(", "")
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
    with SgChrome() as driver:
        driver.get(base_url)
        rr = driver.wait_for_request(json_url, timeout=30)
        locations = json.loads(rr.response.body)["properties"]["contentAreas"][
            "userContent"
        ]["content"]["cells"]
        for loc in locations:
            _ = loc["content"]["properties"]["repeatables"][0]
            addr = []
            phone = ""
            for x, ops in enumerate(_["content"]["quill"]["ops"]):
                if not ops["insert"].strip():
                    continue
                if x < 3:
                    addr.append(ops["insert"])
                else:
                    phone = ops["insert"]
                    break

            yield SgRecord(
                page_url=base_url,
                location_name=_["title"]["content"]["quill"]["ops"][0]["insert"],
                street_address=" ".join(addr[:-1]),
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split()[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split()[-1].strip(),
                country_code="CA",
                phone=_p(phone),
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
