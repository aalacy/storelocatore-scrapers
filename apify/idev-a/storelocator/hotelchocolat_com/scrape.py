from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
import re
from sgpostal.sgpostal import parse_address_intl
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
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.hotelchocolat.com"
base_url = "https://www.hotelchocolat.com/uk/chocolate-shops"


def _latlng(markers, name):
    pos = {"lat": "", "lng": ""}
    for marker in markers:
        mm = json.loads(
            marker.split(");")[0].replace("\n", "").replace("map,", '"map",')
        )
        if (
            mm["title"]
            .replace("&#40;", "(")
            .replace("&#41;", ")")
            .replace("&#39;", "'")
            == name
        ):
            pos = mm["position"]
            break
    return pos


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        driver.find_element_by_css_selector(
            'select#dwfrm_storelocator_country option[value="all"]'
        ).click()
        soup = bs(driver.page_source, "lxml")
        locations = soup.select("div.store-information")
        markers = soup.find(
            "script", string=re.compile(r"new google.maps.Marker\(")
        ).string.split("new google.maps.Marker(")[1:]
        for _ in locations:
            _addr = [
                aa.text.strip()
                for aa in _.select_one("p.store-phone").find_previous_siblings("p")[
                    ::-1
                ]
            ]
            if "Hotel Chocolat" in _addr[0]:
                del _addr[0]
            raw_address = " ".join(_addr)
            addr = parse_address_intl(raw_address)
            ss = json.loads(_.select_one("a.get-dir-store-detail")["data-gtmdata"])
            _city = ss["city"].replace(".", "")
            if _city in raw_address:
                idx = raw_address.rfind(_city)
                street_address = raw_address[:idx]
            else:
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
            if not street_address:
                street_address = _addr[0]
            if (
                len(street_address.split()) == 2
                and street_address.split()[0] == "Unit"
                and ss.get("postalCode")
                and ss.get("postalCode") in raw_address
            ):
                idx = raw_address.rfind(ss.get("postalCode"))
                street_address = raw_address[:idx]
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in _.select("div.working-hours > p")
            ]
            location_type = [
                lt.text.strip() for lt in _.select("div.locationType div.feature-block")
            ]
            page_url = locator_domain + _.select_one("a.store-details-link")["href"]
            coord = _latlng(markers, ss["name"])
            state = addr.state
            if state and state.replace("-", "").isdigit():
                state = ""
            yield SgRecord(
                page_url=page_url,
                store_number=ss["ID"],
                location_name=ss["name"],
                street_address=street_address,
                city=ss["city"],
                state=state,
                zip_postal=ss.get("postalCode"),
                country_code=addr.country,
                phone=_.select_one("p.store-phone").text.strip(),
                latitude=coord["lat"],
                longitude=coord["lng"],
                location_type=", ".join(location_type),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
