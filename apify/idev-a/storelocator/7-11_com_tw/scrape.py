from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("pcsc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

_header1 = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

locator_domain = "https://emap.pcsc.com.tw"
base_url = "https://emap.pcsc.com.tw/lib/areacode.js"
city_url = "https://emap.pcsc.com.tw/EMapSDK.aspx"


def _c(v):
    _v = v.split(".")[0]
    return _v[:-6] + "." + _v[-6:]


def fetch_data():
    with SgRequests() as session:
        for city in session.get(base_url, headers=_headers).text.split("new AreaNode(")[
            1:
        ]:
            city_name = city.split(",")[0][1:-1]
            code = city.strip().split(",")[-2].strip().split(")")[0][1:-1]
            if not city_name:
                continue
            data = {"commandid": "GetTown", "cityid": str(code), "leftMenuChecked": ""}
            towns = bs(
                session.post(city_url, headers=_header1, data=data).text, "lxml"
            ).select("GeoPosition")
            for town in towns:
                data1 = {
                    "commandid": "SearchStore",
                    "city": city_name,
                    "town": town.townname.text,
                    "roadname": "",
                    "ID": "",
                    "StoreName": "",
                    "SpecialStore_Kind": "",
                    "leftMenuChecked": "",
                    "address": "",
                }
                locations = bs(
                    session.post(city_url, headers=_header1, data=data1).text, "lxml"
                ).select("GeoPosition")
                logger.info(f"[{city_name}] [{town.townname.text}] {len(locations)}")
                for _ in locations:
                    yield SgRecord(
                        page_url=base_url,
                        store_number=_.poiid.text.strip(),
                        location_name=_.poiname.text.strip(),
                        street_address=_.address.text.replace(city_name, ""),
                        city=city_name,
                        country_code="Taiwan",
                        phone=_.telno.text.strip(),
                        latitude=_c(_.y.text),
                        longitude=_c(_.x.text),
                        locator_domain=locator_domain,
                        raw_address=_.address.text.strip(),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
