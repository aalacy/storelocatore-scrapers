from typing import Iterable
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicZipSearch, Grain_8
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pendleton")

locator_domain = "https://www.pendleton-usa.com"
base_url = "https://www.pendleton-usa.com/search-stores/?address={}&retailStore=true&outletStore=true&otherStore=false"

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def _hr(sp1, name):
    hours = []
    street = ""
    for _ in sp1.select("div.store-content-information"):
        if (
            _.select_one(".store-name")
            .text.replace("&#35;", "#")
            .strip()
            .split("#")[-1]
            == name.split("#")[-1]
        ):
            for hh in _.select_one("span.hour-breaks").stripped_strings:
                if "open" in hh.lower():
                    continue
                if "call" in hh.lower():
                    break
                hours.append(hh)
            street = list(_.address.stripped_strings)[0]
            break
    return hours, street


def fetch_records(http: SgRequests, search: DynamicZipSearch) -> Iterable[SgRecord]:
    maxZ = search.items_remaining()
    for zip in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()

        sp1 = bs(http.post(base_url.format(zip), headers=_headers).text, "lxml")
        locs = []
        if sp1.text:
            locs = json.loads(
                sp1.select_one("div.storeJSON")["data-storejson"].replace("&quot;", '"')
            )
            for _ in locs:
                hours, street = _hr(sp1, _["name"])
                street_address = _["address1"]
                if not street_address:
                    street_address = street
                yield SgRecord(
                    page_url="https://www.pendleton-usa.com/find-stores/",
                    store_number=_["name"].split("#")[-1],
                    location_name=_["name"],
                    street_address=street_address.replace(", ", " ").strip(),
                    city=_["city"],
                    state=_["stateCode"],
                    zip_postal=_["postalCode"],
                    phone=_["phone"],
                    country_code="USA",
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    hours_of_operation="; ".join(hours),
                )
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        logger.info(f"[{zip}] {progress} [{len(locs)}]")


if __name__ == "__main__":
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], granularity=Grain_8()
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
