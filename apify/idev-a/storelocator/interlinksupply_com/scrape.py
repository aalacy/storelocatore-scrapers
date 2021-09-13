from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("interlinksupply")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://interlinksupply.com/"
    base_url = "https://interlinksupply.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        script = soup.find(
            "script", string=re.compile(r"function initialize()")
        ).string.strip()
        store_number = 1
        coords = {}
        while True:
            _marker = script.split(f"var store_{store_number}=new google.maps.LatLng(")
            _marker_next = script.split(
                f"var store_{store_number+1}=new google.maps.LatLng("
            )
            logger.info(f"store_number {store_number}")
            if len(_marker) == 1 and len(_marker_next) == 1:
                break
            if len(_marker) == 1:
                store_number += 1
                continue
            _info = script.split(
                f"var infowindow_{store_number} = new google.maps.InfoWindow("
            )
            phone = _info[1].split("});")[0].split("Ph:")[1].strip()[:-1].strip()
            coords[phone] = _marker[1].split(");")[0].split(",")
            store_number += 1

        logger.info(f"{len(coords)} coords found")

        locations = soup.select("div.mapListingContainer .col-25-percent")
        logger.info(f"{len(locations)} locations  found")
        for _ in locations:
            block = list(_.stripped_strings)
            latitude = longitude = phone = ""
            raw_address = ""
            for x, bb in enumerate(block):
                if bb.startswith("Ph:"):
                    phone = bb.split(":")[-1].replace("Ph", "").strip()
                    if coords.get(phone):
                        latitude = coords[phone][0]
                        longitude = coords[phone][1]
                    raw_address = " ".join(block[1:x])
                    break
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                location_name=block[0],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.PHONE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
