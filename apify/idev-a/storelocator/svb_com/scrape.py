from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re
import json

logger = SgLogSetup().get_logger("svb")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.svb.com"
base_url = "https://www.svb.com/locations"


def _d(_, country, url):
    _title = _.select_one("div.collapsible-boxes__item-title")
    _addr = list(_.p.stripped_strings)
    raw_address = " ".join(_addr).split("Get")[0]
    addr = parse_address_intl(raw_address + ", " + country)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2

    city = addr.city
    state = addr.state
    if country == "US":
        _addr = parse_address_intl(_title.text.strip())
        if _addr.city:
            city = _addr.city
        if _addr.state:
            state = _addr.state
    phone = ""
    if _.find("a", href=re.compile(r"tel:")):
        phone = _.find("a", href=re.compile(r"tel:")).text.strip()
    try:
        coord = json.loads(_title["data-map-coord"])
    except:
        coord = {"latitude": "", "longitude": ""}
    hours = ""
    _hr = _.find("li", string=re.compile(r"Branch hours are"))
    if _hr:
        hours = _hr.text.split("Branch hours are")[-1].split("(")[0].strip()
    location_type = []
    if _.caption:
        caption = _.caption.text.lower().strip()
        if "office" in caption:
            location_type.append("office")
        if "atm" in caption:
            location_type.append("atm")
    if "Corporate office only" in _.text:
        location_type = ["corporate office"]
    if _.find("span", {"class": re.compile(r"fa-university")}):
        location_type = ["branch"]

    return SgRecord(
        page_url=f"{url}&office_id={_title['data-id']}",
        store_number=_title["data-id"],
        location_name=_title.text.strip(),
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=addr.postcode,
        country_code=country,
        location_type=", ".join(location_type),
        phone=phone,
        latitude=coord["latitude"],
        longitude=coord["longitude"],
        locator_domain=locator_domain,
        hours_of_operation=hours,
        raw_address=raw_address,
    )


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        for option in soup.select("select#ddlStates option"):
            if not option.get("value"):
                continue
            url = f"https://www.svb.com/locations?r_id={option.get('value')}"
            logger.info(url)
            locations = bs(session.get(url, headers=_headers).text, "lxml").select(
                "ul.collapsible-boxes > li"
            )
            for _ in locations:
                yield _d(_, "US", url)

        for option in soup.select("select#ddlCountries option"):
            if not option.get("value"):
                continue
            url = f"https://www.svb.com/locations?c_id={option.get('value')}"
            logger.info(url)
            locations = bs(session.get(url, headers=_headers).text, "lxml").select(
                "ul.collapsible-boxes > li"
            )
            for _ in locations:
                yield _d(_, option.get("value"), url)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            if rec:
                writer.write_row(rec)
