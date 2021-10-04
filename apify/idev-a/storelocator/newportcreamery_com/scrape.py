from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
import json
import time
from sgscrape.sgpostal import parse_address_intl
import ssl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

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


def _hours_phone(temp, street, state):
    hours = []
    phone = ""
    postcode = ""
    name = ""
    _street = street.split(" ")[0].strip()
    for tt in temp:
        if state.lower() in tt[0].lower() and _street in tt[-4]:
            postcode = tt[-4].split(" ")[-1].strip()
            name = tt[0]
            for x, hh in enumerate(tt):
                if _phone(hh):
                    hours = tt[x + 1 :]
                    phone = hh
                    break
    return hours, phone, postcode, name


def fetch_data():
    locator_domain = "https://www.newportcreamery.com/"
    page_url = "https://www.newportcreamery.com/locations"
    base_url = "https://siteassets.parastorage.com/pages/pages/thunderbolt?beckyExperiments=specs.thunderbolt.seoFriendlyDropDownMenu"
    with SgChrome() as driver:
        driver.get(page_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests[::-1]:
                logger.info(f"-- running -- {rr.url}")
                if rr.url.startswith(base_url) and rr.response:
                    _json = json.loads(rr.response.body)
                    if (
                        "props" not in _json
                        or "WRchTxt7-t1i" not in _json["props"]["render"]["compProps"]
                    ):
                        continue
                    try:
                        exist = True
                        locations = _json["props"]["render"]["compProps"]
                        temp = list(
                            bs(
                                locations["WRchTxt7-t1i"]["html"], "lxml"
                            ).stripped_strings
                        )
                        blocks = []
                        store = []
                        for x, tt in enumerate(temp):
                            if x == len(temp) - 1:
                                store.append(tt)
                            if tt == "\u200b" or x == len(temp) - 1:
                                if store:
                                    blocks.append(store)
                                store = []
                                continue
                            store.append(tt)
                        logger.info(f"{len(locations)} blocks found")
                        for key, value in locations.items():
                            if not key.startswith("comp-"):
                                continue
                            if "mapData" not in value:
                                continue
                            logger.info(
                                f'{len(value["mapData"]["locations"])} locations found'
                            )
                            for _ in value["mapData"]["locations"]:
                                addr = parse_address_intl(_["address"])
                                street_address = addr.street_address_1
                                if addr.street_address_2:
                                    street_address += " " + addr.street_address_2
                                if "181 Bellevue Avenue" in street_address:
                                    street_address = "7679 Post Road"
                                hours, phone, zip_postal, name = _hours_phone(
                                    blocks, street_address, addr.state
                                )
                                city = name.split(",")[0]
                                state = name.split(",")[-1].strip()
                                yield SgRecord(
                                    page_url=page_url,
                                    location_name=f"{name}",
                                    street_address=street_address,
                                    city=city,
                                    state=state,
                                    zip_postal=zip_postal,
                                    country_code="US",
                                    phone=phone,
                                    locator_domain=locator_domain,
                                    latitude=_["latitude"],
                                    longitude=_["longitude"],
                                    hours_of_operation="; ".join(hours).replace(
                                        "–", "-"
                                    ),
                                )
                    except:
                        import pdb

                        pdb.set_trace()
                    break


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
