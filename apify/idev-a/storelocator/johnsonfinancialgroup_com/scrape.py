from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("johnsonfinancialgroup")

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.johnsonfinancialgroup.com",
    "referer": "https://www.johnsonfinancialgroup.com/locations/",
    "request-context": "appId=cid-v1:072d82c5-e65c-41d4-b566-49c634c0905a",
    "x-requested-with": "XMLHttpRequest",
    "request-id": "|eJrtn.VwbqP",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.johnsonfinancialgroup.com"
base_url = "https://www.johnsonfinancialgroup.com/api/LocationMapApi/GetMapLocations"


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            payload = {
                "Page": page,
                "PageSize": 500,
                "Filters": {
                    "query": "",
                    "branches": "true",
                    "surchargeFreeAtms": "false",
                    "driveUpAtms": "false",
                },
                "Geolocation": {"Lat": 37.09024, "Lng": -95.712891},
            }
            locations = session.post(base_url, headers=_headers, json=payload).json()[
                "Results"
            ]
            logger.info(f"[{page}] {len(locations)}")
            if not locations:
                break
            page += 1
            for _ in locations:
                hours = []
                page_url = ""
                if _["DetailsUrl"]:
                    page_url = locator_domain + _["DetailsUrl"]
                    logger.info(page_url)
                    sp1 = bs(
                        session.get(page_url, headers=_headers).text,
                        "lxml",
                    )
                    hours = [
                        ": ".join(hh.stripped_strings)
                        for hh in sp1.select("table.hours-table")[0].select("tr")
                    ]
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["Name"],
                    street_address=_["Street"],
                    city=_["City"],
                    state=_["State"],
                    zip_postal=_["Zip"],
                    country_code="US",
                    phone=_["Phone"],
                    latitude=_["Latitude"],
                    longitude=_["Longitude"],
                    location_type=_["Type"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
