from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
import us

logger = SgLogSetup().get_logger("")

locator_domain = "http://www.kaboom.com/"
base_url = "https://www.kaboom.com/locations"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


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


def _url(locs, ID):
    for loc in locs:
        if loc["id"] == ID:
            return locator_domain + loc["route"]


def get_country_by_code(code=""):
    if us.states.lookup(code):
        return "US"
    elif code in ca_provinces_codes:
        return "CA"
    else:
        return "<MISSING>"


def fetch_data():
    with SgRequests() as session:
        data = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("window.__BOOTSTRAP_STATE__ =")[1]
            .split("</script>")[0]
            .strip()[:-1]
        )
        locs = data["siteData"]["pagesMeta"]
        locations = data["siteData"]["page"]["properties"]["contentAreas"][
            "userContent"
        ]["content"]["cells"]
        for loc in locations[1:]:
            _ = loc["content"]["properties"]["repeatables"][0]
            phone = []
            if type(_["text"]["content"]) == str:
                continue

            no_loc = False
            blocks = _["text"]["content"]["quill"]["ops"]
            for x, ops in enumerate(blocks):
                tt = ops["insert"].strip()
                if not tt:
                    continue
                if "Click" in tt:
                    no_loc = True
                    break
                if x < len(blocks) - 2 and "(" not in tt:
                    pass
                else:
                    phone.append(tt)

            if no_loc:
                continue

            location_type = ""
            try:
                if (
                    "temporarily closed"
                    in _["callout"]["content"]["quill"]["ops"][0]["insert"]
                ):
                    location_type = "temporarily closed"
            except:
                pass

            page_url = _url(locs, _["image"]["link"]["link"]["page"]["pageID"])
            logger.info(page_url)
            info = json.loads(
                session.get(page_url, headers=_headers)
                .text.split("window.__BOOTSTRAP_STATE__ =")[1]
                .split("</script>")[0]
                .strip()[:-1]
            )["siteData"]["page"]["properties"]["contentAreas"]["userContent"][
                "content"
            ][
                "cells"
            ][
                -1
            ][
                "content"
            ][
                "properties"
            ]
            loc_info = info["mapConfig"]["location"]
            hours = []
            for hh in info["hoursConfig"]["content"]["quill"]["ops"]:
                if not hh["insert"].strip():
                    continue
                hours.append(hh["insert"].strip())

            try:
                latitude = loc_info["lat"]
                longitude = loc_info["lng"]
            except:
                latitude = longitude = ""

            addr = parse_address_intl(loc_info["formatted_address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            city = addr.city
            state = addr.state
            zip_postal = addr.postcode
            if city and city == "Toronto On M1L":
                city = "Toronto"
                state = "ON"
                zip_postal = "M1L"
            yield SgRecord(
                page_url=page_url,
                location_name=_["title"]["content"]["quill"]["ops"][0][
                    "insert"
                ].strip(),
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=get_country_by_code(state),
                latitude=latitude,
                longitude=longitude,
                location_type=location_type,
                phone=_p("".join(phone)),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("\n", "; "),
                raw_address=loc_info["formatted_address"],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
