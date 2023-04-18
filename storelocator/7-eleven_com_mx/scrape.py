from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs
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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": None,
    "Content-Type": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Host": "app.7-eleven.com.mx:8443",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.7-eleven.com.mx"
base_url = "https://app.7-eleven.com.mx:8443/web/services/tiendas?key=xc3d"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        locations = json.loads(bs(driver.page_source, "lxml").text)["results"]
        for _ in locations:
            addr = _["full_address"].replace("S/N", "").split(",")
            if "C.P" in addr[-1] or addr[-1].strip().isdigit():
                zip_postal = addr[-1].replace("C.P.", "").replace("C.P", "")
                del addr[-1]
            yield SgRecord(
                store_number=_["id"],
                location_name=_["name"],
                street_address=", ".join(addr[:-2]),
                city=addr[-2].strip(),
                state=addr[-1].strip(),
                zip_postal=zip_postal,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Mexico",
                locator_domain=locator_domain,
                hours_of_operation=_["open_hours"],
                raw_address=_["full_address"].replace("S/N", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
