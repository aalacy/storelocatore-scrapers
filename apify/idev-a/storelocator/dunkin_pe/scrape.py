from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("dunkin")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dunkin.pe"
base_url = "https://dunkin.pe/locales"


def _coord(links, raw_address):
    lat = lng = ""
    for link in links:
        _link = link.split("tag:")[0]
        if raw_address in _link:
            lat = (
                _link.split("latitude")[1]
                .split(",")[0]
                .replace('"', "")
                .replace(":", "")
            )
            lng = (
                _link.split("longtitude")[1]
                .split(",")[0]
                .replace('"', "")
                .replace(":", "")
            )
            if lat == "cb":
                lat = ""
                lng = ""
            break

    return lat, lng


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.find(
            "script", string=re.compile(r"window\.__NUXT__")
        ).string.split("{storelocator_id:")[1:]
        logger.info(f"{len(links)} found")
        locations = soup.select("div.location-card")
        for _ in locations:
            raw_address = _.select_one(
                "div.location-body div.schedule-body"
            ).text.strip()
            addr = parse_address_intl(raw_address + ", Peru")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            street_address = (
                street_address.replace("Peru", "").replace("Lima", "").strip()
            )
            if street_address.isdigit():
                street_address = raw_address.split("INT")[0]
            hours_of_operation = ""
            _hr = _.find("b", string=re.compile(r"Horario de tienda"))
            if _hr:
                hours_of_operation = _hr.find_next_sibling().text.strip()
            phone = ""
            if _.select_one("a.call-order span"):
                phone = _.select_one("a.call-order span").text.strip()
                if phone == "-":
                    phone = ""
            lat, lng = _coord(links, raw_address)
            yield SgRecord(
                page_url=base_url,
                store_number=_["for"],
                location_name=_.select_one("div.location-header").text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Peru",
                phone=phone,
                locator_domain=locator_domain,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
