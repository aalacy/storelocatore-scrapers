from typing import Iterable

from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_4
import urllib.parse
import json
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("sej")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

base_url = "https://ml.its-mo.com/p/en/711map/zdcemaphttp.cgi"
locator_domain = "https://www.sej.co.jp/in/en.html"


def params(lat, lng):
    return {
        "target": "http://vstorenaviweb.vmc.zdc.local/cgi/store_nearsearch.cgi?from=js&intid=EmapMlSsQ&lang=en&cid=711map&opt=711map&pos=1&cnt=5&lat={}&lon={}&filter=(COL_02:DT:LTE:SYSDATE AND COL_12:1)&ewdist=50000&sndist=50000&knsu=5&exkid=&pflg=1&cols=".format(
            lat, lng
        ),
        "zdccnt": "3",
        "enc": "EUC",
        "encodeflg": "0",
    }


def _v(_, key):
    col = ""
    for ll in _["content"]:
        if ll["col"].lower() == key:
            col = ll["text"]
            break
    return col


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    maxZ = search.items_remaining()
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        locations = json.loads(
            http.get(
                f"{base_url}?{urllib.parse.urlencode(params(lat, lng))}",
                headers=_headers,
            ).text.split("= '")[1][:-2]
        ).get("store_list", [])
        for _ in locations:
            raw_address = _v(_, "addr")
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            page_url = f"https://ml.its-mo.com/p/en/711map/nmap.htm?lat={_['lat']}&lon={_['lon']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["store_id"],
                location_name=_v(_, "name"),
                street_address=street_address,
                city=addr.city,
                zip_postal=addr.postcode,
                country_code="Japan",
                latitude=_["lat"],
                longitude=_["lon"],
                phone=_v(_, "col_07"),
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        logger.info(f"[{lat}, {lng}] [{progress}], {len(locations)}")


if __name__ == "__main__":
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.JAPAN], granularity=Grain_4()
    )
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
