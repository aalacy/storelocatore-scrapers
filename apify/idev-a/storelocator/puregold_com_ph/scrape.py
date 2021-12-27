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

                hours = []
                block = sum([list(pp.stripped_strings) for pp in _.select("p")], [])
                addr = block
                for x, bb in enumerate(block):
                    if "Hours" in bb:
                        addr = block[:x]
                        hours = [bb.split("Hours")[-1].strip()]
                        if not hours and x < len(block) - 1:
                            for hh in block[x + 1 :]:
                                if _p(hh):
                                    break
                                hours.append(hh)
                        break
                    if "Tel" in bb:
                        addr = block[:x]
                        break
                hours_of_operation = "; ".join(hours)
                if hours_of_operation.startswith(":"):
                    hours_of_operation = hours_of_operation[1:]
                raw_address = (
                    " ".join(addr)
                    .replace("'", "")
                    .replace("Sta.rosa", "Sta. rosa")
                    .split("(")[0]
                    .strip()
                )
                addr = parse_address_intl(raw_address + ", Philippines")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                if city:
                    city = (
                        city.replace("Subic Bay Freeport Zone", "")
                        .replace("Guitnang Bayan 1", "")
                        .strip()
                    )
                phone = ""
                if _.select_one("span.telno"):
                    phone = (
                        _.select_one("span.telno")
                        .text.split("/")[0]
                        .replace("'", "")
                        .split("No.")[-1]
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
                name = _.strong.text.split("-")[0].strip()
                location_name = ""
                if name == "PG JR":
                    location_name = "PureGold Jr"
                elif name == "PG EXTRA":
                    location_name = "PureGold Extra"
                elif name == "PPCI":
                    location_name = "PureGold"
                yield SgRecord(
                    page_url=base_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="PH",
                    phone=phone,
                    latitude=coord[0],
                    longitude=coord[1],
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
