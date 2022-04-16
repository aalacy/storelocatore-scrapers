from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.eg/"
base_url = "https://mcdonalds.eg/Stotes"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            latlng = _["store_geocode"].split(",")
            city = (
                _["store_code"]
                .replace("Chill-Out", "")
                .replace("ChillOut", "")
                .split("Airport")[0]
            )
            if city in ["CFC-Mall", "7-Stars", "K13", "R5B"]:
                city = ""
            if (
                "Coast" in city
                or "Club" in city
                or "City Centre" in city
                or "City-Stars" in city
                or "Mall" in city
                or "CFC" in city
            ):
                city = ""
            raw_address = _["store_address"]
            if raw_address == "-":
                raw_address = ""

            addr = parse_address_intl(raw_address + ", Egypt")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            aa = raw_address.split(",")
            if street_address in ["6 One", "#7 Block 1"]:
                street_address = aa[0]
            if street_address in ["28 K", "121", "k 28"]:
                street_address = " ".join(aa[:2])
            if street_address in ["# 14 Egypt"]:
                street_address = raw_address

            if addr.city:
                city = addr.city
            if "Nasr" in raw_address:
                city = "Nasr City"
            if "6 of October" in raw_address:
                city = "6 of October"
            yield SgRecord(
                page_url="https://mcdonalds.eg/learn/about-mcdonalds-egypt/find-restaurant",
                store_number=_["nid"],
                location_name=_["title"],
                street_address=street_address.replace("6 of October", ""),
                city=city.replace("-", " "),
                state=_["store_state"],
                latitude=latlng[0],
                longitude=latlng[1],
                country_code="EG",
                location_type=_["status"],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
