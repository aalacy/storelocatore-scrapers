from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import ssl
import re
from bs4 import BeautifulSoup as bs

ssl._create_default_https_context = ssl._create_unverified_context

locator_domain = "https://www.themelt.com"
base_url = "https://www.themelt.com/locations"
json_url = "https://www.themelt.com/_api/cloud-data/v1/wix-data/collections/query"


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
        rr = driver.wait_for_request(json_url, 30)
        locations = json.loads(rr.response.body)
        for _ in locations["items"]:
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
            street_address = (
                street_address.split("(")[0]
                .split("Between")[0]
                .replace("Westfield Oakridge Mall,", "")
                .replace("Taste Food Hall:", "")
                .replace("at Second St.", "")
                .strip()
            )
            if street_address.endswith(","):
                street_address = street_address[:-1]
            if not street_address:
                street_address = _["address"]

            yield SgRecord(
                page_url=base_url,
                location_name=_["address"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                country_code="US",
                phone=_p(_.get("phone_number")),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )

        sp1 = bs(driver.page_source, "lxml")
        div = sp1.select_one(
            'main div[data-testid="mesh-container-content"]'
        ).findChildren(recursive=False)[-1]
        state = ""
        for pp in div.find_previous_siblings("div"):
            if not pp.p:
                continue
            state = pp.text.strip()
            break
        locs = div.select('div[role="row"]')
        for loc in locs:
            location_name = loc.p.text.strip()
            street1 = loc.h5.text.strip()
            if not street1[0].isdigit():
                street1 = ""
            street2 = loc.select("p")[1].text.split(":")[-1].strip()
            street_address = ""
            if street1:
                street_address = street1
            if street2:
                street_address += " " + street2

            _hr = loc.find("span", string=re.compile(r"^Hours"))
            temp = [
                hh.text.strip()
                for hh in _hr.find_parent("div").find_next_siblings("div")
                if hh.text.strip()
            ]
            hours = []
            ii = int(len(temp) / 2)
            for x in range(0, ii):
                hours.append(f"{temp[x]}: {temp[x+ii]}")

            _pp = loc.find("span", string=re.compile(r"^Phone"))
            phone = ""
            if _pp and _pp.find_parent("div"):
                phone = _pp.find_parent("div").find_next_sibling().text.strip()

            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=location_name,
                state=state,
                country_code="US",
                phone=phone,
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
