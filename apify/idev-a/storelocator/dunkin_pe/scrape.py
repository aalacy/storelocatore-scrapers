from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from pyjsparser import parse
import re
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("dunkin")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dunkin.pe"
base_url = "https://dunkin.pe/locales"


def _coord(links, raw_address):
    is_found = False
    selected_node = None
    latitude = longitude = ""
    try:
        for link in links:
            for prop in link["properties"]:
                if prop["value"].get("value") == raw_address:
                    is_found = True
                    break

            if is_found:
                selected_node = link["properties"]
                break
        for node in selected_node:
            if node["key"]["name"] == "latitude":
                latitude = node["value"]["value"]

            if node["key"]["name"] == "longtitude":
                longitude = node["value"]["value"]
    except:
        pass

    return latitude, longitude


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        res = (
            soup.find("script", string=re.compile(r"window\.__NUXT__"))
            .string.split("stores:")[1]
            .split("stores_positions")[0]
            .strip()[:-1]
        )
        links = parse(res)["body"][0]["expression"]["elements"]
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
            coord = _coord(links, raw_address)
            yield SgRecord(
                page_url=base_url,
                store_number=_["for"],
                location_name=_.b.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Peru",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
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
