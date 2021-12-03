from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("puregold")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://puregold.com.ph"
base_url = "http://puregoldbeta.webtogo.com.ph/store_locator.do"


def _p(val):
    if (
        val
        and val.split("/")[0]
        .replace("–", "-")
        .replace("'", "")
        .replace("(", "")
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
    with SgRequests() as session:
        regions = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "select#region option"
        )
        for region in regions:
            if region.get("value") == "0":
                continue
            locations = bs(
                session.get(
                    f"{base_url}?regionkey={region['value']}", headers=_headers
                ).text,
                "lxml",
            ).select("table.storeLocatorResult td.storeContent")
            logger.info(f"{region['value']}, {len(locations)}")
            for _ in locations:
                if not _.text.strip():
                    continue

                addr = []
                hours = ""
                for pp in _.select("p"):
                    _pp = []
                    for hr in pp.stripped_strings:
                        _hr = hr.strip()
                        if "Hour" in _hr:
                            hours = _hr.split("Hours")[-1].replace(":", "").strip()
                            break
                        if not _hr or _p(_hr):
                            continue
                        _pp.append(_hr)
                    addr.append(" ".join(_pp))
                raw_address = " ".join(addr).replace("'", "").strip()
                addr = parse_address_intl(raw_address + ", Philippines")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                phone = ""
                if _.select_one("span.telno"):
                    phone = (
                        _.select_one("span.telno")
                        .text.split("/")[0]
                        .replace("'", "")
                        .strip()
                    )
                coord = ["", ""]
                if _.select_one("div.viewmap a"):
                    coord = (
                        _.select_one("div.viewmap a")["onclick"]
                        .split("(")[1]
                        .split(")")[0]
                        .split(",")
                    )
                yield SgRecord(
                    page_url=base_url,
                    location_name=_.strong.text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="PH",
                    phone=phone,
                    latitude=coord[0],
                    longitude=coord[1],
                    locator_domain=locator_domain,
                    hours_of_operation=hours,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
