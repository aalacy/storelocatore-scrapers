from typing import Any
from typing import Dict
from typing import Iterable

from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgwriter import SgWriter

import time

LOCATOR_DOMAIN = "https://www.esbenergy.co.uk/"
PAGE_URL = "https://myevaccount.esbenergy.co.uk/findCharger?"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
HEADERS = {
    "User-Agent": UA,
    "Content-Type": "application/json",
}
UK_BOUNDING_BOX = {
    "northEastLat": 61.061,
    "northEastLng": 2.0919117,
    "southWestLat": 49.674,
    "southWestLng": -8.1775098,
}


def _fetch_station_ids(http: SgRequests) -> Iterable[int]:
    station_records = http.post(
        url="https://myevaccount.esbenergy.co.uk/stationFacade/findStationsInBounds",
        headers=HEADERS,
        json={
            "filterByIsManaged": True,
            "filterByBounds": UK_BOUNDING_BOX,
        },
    ).json()["data"][1]

    return (record["id"] for record in station_records)


def _make_sg_record(station_obj: Dict[str, Any]) -> SgRecord:
    def format_opening_times(opening_times: Dict[str, str]) -> str:
        DAY_OF_WK = "dayOfWeekId"
        START_HR = "startHour"
        END_HR = "endHour"
        MS_PER_SEC = 1000
        hr_range = (
            time.strftime("%H:%M", time.gmtime(int(opening_times[k]) // MS_PER_SEC))
            for k in (START_HR, END_HR)
        )

        return f"{opening_times[DAY_OF_WK]}: {'-'.join(hr_range)}"

    return SgRecord(
        page_url=PAGE_URL,
        location_name=station_obj["caption"],
        street_address=station_obj["addressAddress1"],
        city=station_obj["addressCity"],
        zip_postal=station_obj["addressZipCode"],
        country_code=station_obj["addressCountryIso2Code"],
        store_number=station_obj["id"],
        location_type=station_obj["chargingSpeedId"],
        latitude=station_obj["latitude"],
        longitude=station_obj["longitude"],
        locator_domain=LOCATOR_DOMAIN,
        hours_of_operation=(
            "; ".join(map(format_opening_times, station_obj["openingTimes"]))
            or "Open 24/7"
        ),
        phone=PHONE_NUMBER,
    )


def _fetch_data(http: SgRequests) -> Iterable[SgRecord]:
    station_ids = _fetch_station_ids(http)
    station_objs = (
        http.get(
            url="https://myevaccount.esbenergy.co.uk/stationFacade/findStationById",
            headers=HEADERS,
            params={"stationId": station_id},
        ).json()["data"]
        for station_id in station_ids
    )

    return map(_make_sg_record, station_objs)


def _fetch_phone_number(http: SgRequests) -> str:
    PHONE_PREFIX = "tel:"

    response = http.get(url=LOCATOR_DOMAIN, headers={"User-Agent": UA})
    dom = etree.HTML(response.text)
    try:
        phone_txt = dom.xpath(f"//a[contains(@href, '{PHONE_PREFIX}')]/@href")[0]
    except:
        phone_txt = ""

    return "".join(phone_txt[len(PHONE_PREFIX) :].split())


if __name__ == "__main__":
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests(proxy_country="gb") as http:
            PHONE_NUMBER = _fetch_phone_number(http)
            records = _fetch_data(http)
            for record in records:
                writer.write_row(record)
