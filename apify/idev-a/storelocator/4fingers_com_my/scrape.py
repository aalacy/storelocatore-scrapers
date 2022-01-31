from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re
from sgpostal.sgpostal import parse_address_intl
import dirtyjson as json

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.4fingers.com.my"
base_url = "http://www.4fingers.com.my/Outlets-4FINGERS"


def _coord(locs, name):
    res = None
    for loc in locs:
        if name.lower() in loc[0].lower():
            res = loc
            break

    for loc in locs:
        if name.split(",")[-1].lower() in loc[0].lower():
            res = loc
            break

    if not res:
        for loc in locs:
            if name.split()[-1].lower() in loc[0].lower():
                res = loc
                break

    return res


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locs = json.loads(
            res.split("var locations =")[1]
            .split("var openingsoonlocations")[0]
            .strip()[:-1]
        )
        soup = bs(res, "lxml")
        locations = soup.select("div.child-effect")
        for _ in locations:
            if "Opening" in _.text:
                continue
            _addr = []
            for aa in _.select(
                "div.child-effect div.top-description div.col-xs-10 p.address"
            ):
                if "Landmark" in aa.text:
                    break
                _addr.append(aa.text.strip())

            raw_address = " ".join(_addr)
            if "Malaysia" not in raw_address:
                raw_address += ", Malaysia"
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            _hr = _.find("p", string=re.compile(r"Operation Hours:"))
            hours = ""
            if _hr:
                hours = _hr.find_parent().find_next_sibling().text.strip()

            _pp = _.find("p", string=re.compile(r"Telephone:"))
            phone = ""
            if _hr:
                phone = _pp.find_parent().find_next_sibling().text.strip()
                if phone == "N/A":
                    phone = ""
            name = _.select_one("div.headers-right").text.strip()
            coord = _coord(locs, name)
            if not coord:
                import pdb

                pdb.set_trace()
            yield SgRecord(
                page_url=base_url,
                location_name=name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="MY",
                phone=phone,
                latitude=coord[1],
                longitude=coord[2],
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
