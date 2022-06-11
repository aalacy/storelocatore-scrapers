from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("shopsavmor")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.shopsavmor.com/"
base_url = "https://savmorfoods.storebyweb.com/s/1000-9/api/stores"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["data"]
        logger.info(f"{len(locations)} found")
        for _ in locations:
            addr = _["addresses"][0]
            street_address = addr["street1"]
            if addr["street2"]:
                street_address += " " + addr["street2"]

            phone = ""
            if _.get("phones"):
                phone = _["phones"][0].get("phone")
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=addr["city"],
                state=addr["state"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                zip_postal=addr["postal"],
                country_code=addr["country"],
                phone=phone,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
