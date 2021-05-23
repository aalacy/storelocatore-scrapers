from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
import json
import time
from sgscrape.sgpostal import parse_address_intl
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

logger = SgLogSetup().get_logger("newportcreamery")


def _phone(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def _hours_phone(temp, city, state):
    hours = []
    phone = ""
    _city = city.lower().split(" ")[-1]
    for tt in temp:
        if state.lower() in tt[0].lower() and _city in tt[0].lower():
            for x, hh in enumerate(tt):
                if _phone(hh):
                    hours = tt[x + 1 :]
                    phone = hh
                    break
    return hours, phone


def fetch_data():
    locator_domain = "https://www.newportcreamery.com/"
    page_url = "https://www.newportcreamery.com/locations"
    base_url = "https://siteassets.parastorage.com/pages/pages/thunderbolt?beckyExperiments=specs.thunderbolt.stylableCssPerComponent%3Atrue%2Cspecs.thunderbolt.addressInputAtlasProvider"
    with SgChrome() as driver:
        driver.get(page_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests[::-1]:
                logger.info(f"-- running -- {rr.url}")
                if rr.url.startswith(base_url) and rr.response.body:
                    _json = json.loads(rr.response.body)
                    if (
                        "props" not in _json
                        or "WRchTxt7-t1i" not in _json["props"]["render"]["compProps"]
                    ):
                        continue
                    exist = True
                    locations = _json["props"]["render"]["compProps"]
                    temp = list(
                        bs(locations["WRchTxt7-t1i"]["html"], "lxml").stripped_strings
                    )
                    blocks = []
                    store = []
                    for x, tt in enumerate(temp):
                        if tt == "\u200b" or x == len(temp) - 1:
                            if store:
                                blocks.append(store)
                            store = []
                            continue
                        store.append(tt)
                    logger.info(f"{len(blocks)} blocks found")

                    logger.info(f"{len(locations)} locations found")
                    for key, value in locations.items():
                        if not key.startswith("comp-"):
                            continue
                        if "mapData" not in value:
                            continue
                        for _ in value["mapData"]["locations"]:
                            addr = parse_address_intl(_["address"])
                            street_address = addr.street_address_1
                            if addr.street_address_2:
                                street_address += " " + addr.street_address_2
                            hours, phone = _hours_phone(blocks, addr.city, addr.state)
                            yield SgRecord(
                                page_url=page_url,
                                location_name=f"{addr.city}, {addr.state}",
                                street_address=street_address,
                                city=addr.city,
                                state=addr.state,
                                zip_postal=addr.postcode,
                                country_code="US",
                                phone=phone,
                                locator_domain=locator_domain,
                                latitude=_["latitude"],
                                longitude=_["longitude"],
                                hours_of_operation="; ".join(hours).replace("–", "-"),
                            )

                    break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
