from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from bs4 import BeautifulSoup as bs
import re

logger = SgLogSetup().get_logger("toms.com")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.toms.com"
base_url = "https://www.toms.com/on/demandware.store/Sites-toms-us-Site/en_US/Stores-FindStores?showMap=true&radius=30&categories=&typesStores=&lat={}&long={}"
us_url = "https://www.toms.com/us/toms-stores.html"
us_data = []


def fetch_us():
    with SgRequests() as session:
        soup = bs(session.get(us_url, headers=_headers).text, "lxml")
        links = soup.select("div.experience-commerce_assets-contentTile")
        logger.info(f"{len(links)} found")
        for link in links:
            if not link.select_one("span.c-content-tile__box-title"):
                continue
            hours = []
            _hr = link.find("strong", string=re.compile(r"Store hours", re.IGNORECASE))
            if _hr:
                for hh in _hr.find_parent().find_next_siblings("p"):
                    if not hh.text.strip() or "hour" in hh.text.lower():
                        break
                    hours.append(hh.text.strip())

            _addr = []
            for aa in (
                link.find("strong", string=re.compile(r"Location"))
                .find_parent()
                .find_next_siblings("p")
            ):
                if "Phone" in aa.text:
                    break
                if not aa.text.strip():
                    continue
                _addr.append(aa.text)

            if not _addr[0][0].isdigit():
                del _addr[0]
            phone = ""
            if link.find("", string=re.compile(r"Phone")):
                phone = (
                    link.find("", string=re.compile(r"Phone"))
                    .find_parent("p")
                    .text.replace("Phone", "")
                    .replace("-", "")
                    .strip()
                )
                if not phone:
                    phone = (
                        link.find("strong", string=re.compile(r"Phone"))
                        .find_parent()
                        .find_next_sibling("p")
                        .text.replace("-", "")
                        .strip()
                    )
            if phone:
                phone = phone.replace("\ufeff", "").strip()
            us_data.append(
                dict(
                    page_url=base_url,
                    location_name=link.select_one("span.c-content-tile__box-title")
                    .text.replace("Store Details", "")
                    .strip(),
                    street_address=" ".join(_addr[:-1]),
                    city=_addr[-1].split(",")[0].strip(),
                    state=_addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=_addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )
            )


def _v(pp):
    if pp:
        return (
            pp.replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
            .strip()
        )
    else:
        return ""


def _data(phone):
    for dd in us_data:
        if _v(dd["phone"]) == _v(phone):
            return dd

    return {}


def fetch_data():
    for lat, lng in search:
        with SgRequests() as session:
            locations = session.get(base_url.format(lat, lng), headers=_headers).json()[
                "stores"
            ]
            logger.info(f"[{search.current_country()}] [{lat, lng}] {len(locations)}")
            for _ in locations:
                search.found_location_at(_["latitude"], _["longitude"])
                street_address = _["address1"]
                if _["address2"]:
                    street_address += " " + _["address2"]

                hours = ""
                state = ""
                if _["countryCode"] == "US":
                    dd = _data(_.get("phone"))
                    hours = dd.get("hours_of_operation")
                    state = dd.get("state")
                yield SgRecord(
                    page_url="https://www.toms.com/us/store-locator",
                    store_number=_["ID"],
                    location_name=_["name"],
                    street_address=street_address.replace("\n", "").replace("\r", " "),
                    city=_["city"],
                    state=state,
                    zip_postal=_.get("postalCode"),
                    country_code=_["countryCode"],
                    phone=_.get("phone"),
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    locator_domain=locator_domain,
                    hours_of_operation=hours,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])
        fetch_us()
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
