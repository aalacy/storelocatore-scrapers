from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
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

locator_domain = "http://www.dunkindonuts.co.kr"
base_url = "http://www.dunkindonuts.co.kr/store/list_ajax.php?ScS=&ScG=&ScWord="


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        locations = json.loads(driver.find_element_by_css_selector("body").text)["list"]
        for _ in locations:
            hours = []
            hours.append(f"주중: {_['operationtimeA']}")
            if _.get("operationtimeB"):
                hours.append(f"주말: {_['operationtimeB']}")
            yield SgRecord(
                page_url="http://www.dunkindonuts.co.kr/store/map.php",
                store_number=_["storeCode"],
                location_name=_["name"],
                street_address=_["address3"],
                state=_["address1"],
                city=_["address2"],
                latitude=_["pointX"],
                longitude=_["pointY"],
                country_code="kr",
                phone=_["tel"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("&#58;", ":"),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
