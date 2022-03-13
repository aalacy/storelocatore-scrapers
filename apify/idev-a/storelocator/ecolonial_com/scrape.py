from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from urllib.parse import urlencode
import re
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("ecolonial")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://ecolonial.com"
base_url = "https://ecolonial.com/wp-admin/admin-ajax.php?"
types = ["daily", "monthly"]


def _pp(val):
    return "".join(
        [vv for vv in val.split(";")[0] if vv.isdigit() or vv == "-" or vv == " "]
    ).strip()


def fetch_data():
    with SgRequests() as session:
        _from = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
        _to = (datetime.now() + timedelta(hours=3, minutes=30)).strftime(
            "%m/%d/%Y %I:%M:%S %p"
        )
        for _type in types:
            params = dict(
                action="mapmarkers",
                ne_lat="43.35468582449911",
                ne_lng="-67.61070150457917",
                sw_lat="37.768048573165224",
                sw_lng="-88.92417806707917",
                zoom="7",
                reset="0",
                formaction="search",
                type=_type,
                locationsearch="",
                period_from=_from,
                period_to=_to,
            )
            url = base_url + urlencode(params)
            locations = session.get(url, headers=_headers).json()
            logger.info(f"[{_type}] {len(locations)} found")
            for _ in locations:
                page_url = f"https://ecolonial.com/park-with-us/parking-locator/?detail=1&loc=en&id={_['remoteid']}"
                logger.info(page_url)

                _params = dict(
                    action="facility",
                    id=_["id"],
                    type=_type,
                    period_from=_from,
                    period_to=_to,
                )
                _url = base_url + urlencode(_params)
                sp1 = bs(session.get(_url, headers=_headers).text, "lxml")
                _p = sp1.find("b", string=re.compile(r"^Phone:"))
                phone = ""
                if _p:
                    phone = _p.find_next_sibling().text.strip()
                hours = [hh.text.strip() for hh in sp1.select("div.openhours p.intend")]
                raw_address = (
                    sp1.find("b", string=re.compile(r"^Address:"))
                    .find_next_sibling()
                    .text.strip()
                )
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                state = addr.state

                if not state and sp1.find("b", string=re.compile(r"^GPS Address:")):
                    gps_address = (
                        sp1.find("b", string=re.compile(r"^GPS Address:"))
                        .find_next_sibling()
                        .text.strip()
                    )
                    state = parse_address_intl(gps_address).state
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=addr.city,
                    state=state,
                    zip_postal=addr.postcode,
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code="US",
                    phone=_pp(phone),
                    location_type=_type,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours)
                    .replace("\n", "")
                    .replace("\t", ""),
                    raw_address=raw_address,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_TYPE, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
