from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.danielsjewelers.com"
base_url = "https://admin.danielsjewelers.com/storelocator/index/stores/?type=all"

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["storesjson"]
        for _ in locations:
            page_url = (
                f"https://www.danielsjewelers.com/stores/{_['rewrite_request_path']}"
            )
            detail_url = f"https://admin.danielsjewelers.com/storelocator/index/Storedetail/?locatorId={_['rewrite_request_path']}&type=store"
            logger.info(detail_url)
            _ = session.get(detail_url, headers=_headers).json()["storesjson"][0]
            hours = []
            for day in days:
                day = day.lower()
                if _.get(f"{day}_open"):
                    start = _.get(f"{day}_open")
                    end = _.get(f"{day}_close")
                    hours.append(f"{day}: {start} - {end}")

            street_address = _["address"]
            if "USA" in street_address:
                street_address = " ".join(street_address.split(",")[:-3])
            yield SgRecord(
                page_url=page_url,
                store_number=_["locator_id"],
                location_name=_["store_name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zipcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=_["country_id"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
