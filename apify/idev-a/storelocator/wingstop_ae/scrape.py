from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
import re

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.wingstop.ae"
base_url = "https://www.wingstop.ae/location"


def _coord(idx, coords):
    for x, latlng in enumerate(coords):
        if idx == x:
            coord = latlng.split(";")[0][1:-1].split(",")
            return coord
    return ["", ""]


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        coords = res.split("= new google.maps.LatLng")[1:]
        soup = bs(res, "lxml")
        locations = soup.select("div.address-content-location")
        for x, _ in enumerate(locations):
            block = list(_.p.stripped_strings)
            phone = ""
            if _.find("a", href=re.compile(r"tel:")):
                phone = _.find("a", href=re.compile(r"tel:")).text.strip()
            _addr = []
            for bb in block[1:]:
                if "Toll" in bb or "Ph:" in bb or "Ph :" in bb:
                    break
                _addr.append(bb.strip())
            if "Wingstop" in _addr[0]:
                del _addr[0]
            raw_address = " ".join(_addr).replace("\n", " ").replace("UAE", "").strip()
            if raw_address.endswith(","):
                raw_address = raw_address[:-1]
            addr = parse_address_intl(raw_address + ", United Arab Emirates")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours_of_operation = (
                block[0]
                .replace("\n", "; ")
                .replace("(No Dine-in)", "")
                .replace("(Takeaway & Delivery Only)", "")
            )
            if hours_of_operation and "shop no" in hours_of_operation.lower():
                hours_of_operation = ""
            coord = _coord(x, coords)
            city = addr.city
            if "Khalifa City" in raw_address:
                city = "Khalifa City"
            yield SgRecord(
                page_url=base_url,
                location_name=_.h4.text.strip(),
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="UAE",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=" ".join(
                    [aa.strip() for aa in hours_of_operation.split() if aa.strip()]
                ),
                raw_address=" ".join(
                    [aa.strip() for aa in raw_address.split() if aa.strip()]
                ),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
