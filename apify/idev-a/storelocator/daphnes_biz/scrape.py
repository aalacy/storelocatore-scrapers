from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://daphnes.biz"
base_url = "https://easylocator.net/ajax/search_by_lat_lon_geojson/daphnes/34.0494/-118.2641/5000/1500/null/null"
page_url = "https://daphnes.biz/locations/"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["physical"]
        for store in locations:
            _ = store["properties"]
            street_address = _["street_address"]
            if _["street_address_line2"]:
                street_address += " " + _["street_address_line2"]
            hours = []
            for hh in bs(_["additional_info"], "lxml").stripped_strings:
                if "hour" in hh.lower():
                    continue
                if "online" in hh.lower():
                    break
                hours.append(hh.strip())
            if hours and "coming soon" in hours[0].lower():
                continue
            if hours and "temporary closed" in hours[0].lower():
                hours = []
            location_type = ""
            if "temporary closed" in _["name"].lower():
                location_type = "temporary closed"
            yield SgRecord(
                page_url=page_url,
                store_number=_["location_number"],
                location_name=_["name"].strip().split("-")[0],
                street_address=street_address,
                city=_["city"],
                state=_["state_province"],
                zip_postal=_["zip_postal_code"],
                latitude=_["lat"],
                longitude=_["lon"],
                country_code=_["country"],
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
