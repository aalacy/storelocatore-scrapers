from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgwriter import SgWriter


def _fetch_station_ids(http: SgRequests) -> List[int]:
    station_records = http.post(
        url="https://myevaccount.esbenergy.co.uk/stationFacade/findStationsInBounds",
        headers=HEADERS,
        json={
            "filterByIsManaged": True,
            "filterByBounds": UK_BOUNDING_BOX,
        },
    ).json()["data"][1]

    return [record["id"] for record in station_records]


def _make_sg_record(station_obj: Dict[str, Any]) -> SgRecord:
    return SgRecord(
        page_url=PAGE_URL,
        location_name=station_obj["caption"],
        street_address=station_obj["addressAddress1"],
        city=station_obj["addressCity"],
        country_code=station_obj["addressCountryIso3Code"],
        store_number=station_obj["id"],
        location_type=station_obj["chargingSpeedId"],
        latitude=station_obj["latitude"],
        longitude=station_obj["longitude"],
        locator_domain=LOCATOR_DOMAIN,
    )


def _fetch_data(http: SgRequests) -> Iterable[SgRecord]:
    station_ids = _fetch_station_ids(http)
    station_objs = http.post(
        url="https://myevaccount.esbenergy.co.uk/stationFacade/findStationsByIds",
        headers=HEADERS,
        json={"filterByIds": station_ids},
    ).json()["data"][1]

    return map(_make_sg_record, station_objs)


if __name__ == "__main__":
    LOCATOR_DOMAIN = "https://www.esbenergy.co.uk/"
    PAGE_URL = "https://myevaccount.esbenergy.co.uk/stationFacade/findStationsByIds"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "Content-Type": "application/json",
    }
    UK_BOUNDING_BOX = {
        "northEastLat": 51.599717874282874,
        "northEastLng": 0.08654981616212254,
        "southWestLat": 51.40952366267913,
        "southWestLng": -0.3381404304199287,
    }

    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests() as http:
            records = _fetch_data(http)
            for record in records:
                writer.write_row(record)
