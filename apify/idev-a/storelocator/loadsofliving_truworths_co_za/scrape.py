from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://loadsofliving.truworths.co.za/"
base_url = "https://loadsofliving.truworths.co.za/ccstore/v1/assembler/pages/Default/storeSearch?Ns=store.geocode({},{})&Nr=AND(product.active:1)&Nfg=store.geocode%7C{}%7C{}%7C500"


def fetch_records(http, search):
    for lat, lng in search:
        locations = http.get(
            base_url.format(lat, lng, lat, lng), headers=_headers
        ).json()["resultsList"]["records"]
        logger.info(f" [{lat, lng}] {len(locations)}")
        for loc in locations:
            _ = loc["attributes"]
            search.found_location_at(lat, lng)
            if _.get("store.address2"):
                street_address = _["store.address2"][0]
            elif _.get("store.address1"):
                street_address = _["store.address1"][0]

            phone = ""
            if _.get("store.telephone"):
                phone = _["store.telephone"][0]
            if phone == "0" or phone == "-":
                phone = ""
            coord = _["store.geocode"][0].split(",")
            search.found_location_at(coord[1], coord[0])
            zip_postal = _["store.postalCode"][0]
            if zip_postal == "0":
                zip_postal = ""
            yield SgRecord(
                page_url="https://loadsofliving.truworths.co.za/store-location",
                location_name=_["store.name"][0],
                store_number=_["store.id"][0],
                street_address=street_address,
                city=_["store.city"][0].split(",")[0],
                zip_postal=zip_postal,
                country_code="South Africa",
                location_type=", ".join(_["store.companyName"]),
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgRequests() as http:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.SOUTH_AFRICA], granularity=Grain_8()
        )
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
            )
        ) as writer:
            for rec in fetch_records(http, search):
                writer.write_row(rec)
