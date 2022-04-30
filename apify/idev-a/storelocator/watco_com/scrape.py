from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import dirtyjson as json
import re
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("watco")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.watco.com"
base_url = "https://www.watco.com/Leaflet_Map_11-05-2020/data/Labels_5.js"
terminal_urls = [
    {
        "url": "https://www.watco.com/Leaflet_Map_11-05-2020/data/ContractTerminalLocations_0.js",
        "str": "var json_ContractTerminalLocations_0 =",
    },
    {
        "url": "https://www.watco.com/Leaflet_Map_11-05-2020/data/MerchantTerminalLocations_1.js",
        "str": "var json_MerchantTerminalLocations_1 =",
    },
    {
        "url": "https://www.watco.com/Leaflet_Map_11-05-2020/data/MechanicalLocations_3.js",
        "str": "var json_MechanicalLocations_3 =",
    },
]

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
    return (
        val.split(":")[-1]
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        links = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var json_Labels_5 =")[1]
            .strip()
        )["features"]
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["properties"]["descriptio"]
            logger.info(page_url)
            res = session.get(page_url, headers=_headers)
            if res.status_code != 200:
                continue
            sp1 = bs(res.text, "lxml")
            if sp1.find("h4", string=re.compile(r"^Operations")):
                addr = list(
                    sp1.find("h4", string=re.compile(r"^Operations"))
                    .find_parent()
                    .stripped_strings
                )[1:]
                street_address = addr[0]
                city = addr[1].split(",")[0].strip()
                state = addr[1].split(",")[1].strip().split(" ")[0].strip()
                zip_postal = addr[1].split(",")[1].strip().split(" ")[-1].strip()
                phone = addr[-1]
            else:
                continue
            yield SgRecord(
                page_url=page_url,
                location_name=link["properties"]["Name"],
                street_address=street_address.replace("–", "-"),
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                latitude=link["geometry"]["coordinates"][1],
                longitude=link["geometry"]["coordinates"][0],
            )

        for terminal in terminal_urls:
            links = json.loads(
                session.get(terminal["url"], headers=_headers)
                .text.split(terminal["str"])[1]
                .strip()
            )["features"]
            logger.info(f"{len(links)} found")
            for link in links:
                info = bs(link["properties"]["Name"], "lxml")
                if not link["properties"]["description"]:
                    continue
                _addr = list(
                    bs(link["properties"]["description"], "lxml").stripped_strings
                )
                phone = ""
                if _p(_addr[-1]):
                    phone = _addr[-1].split(":")[-1].strip()
                    del _addr[-1]
                addr = parse_address_intl(" ".join(_addr))
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                country_code = addr.country
                if not country_code:
                    if addr.state in ca_provinces_codes:
                        country_code = "CA"
                    else:
                        country_code = "US"
                page_url = info.a["href"]
                yield SgRecord(
                    page_url=page_url,
                    location_name=info.h2.text.strip(),
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code=country_code,
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=link["geometry"]["coordinates"][1],
                    longitude=link["geometry"]["coordinates"][0],
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            record_id=SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
