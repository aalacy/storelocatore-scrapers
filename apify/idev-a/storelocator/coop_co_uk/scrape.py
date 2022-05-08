from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("coop")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.coop.co.uk"
    base_url = "https://www.coop.co.uk/store-finder/api/locations/food?location=51.376165%2C-0.098234&distance={}&min_distance={}&min_results=1&format=json"
    distance = 0
    interval = 3000
    total = 0
    _urls = []
    while True:
        with SgRequests(proxy_country="us") as session:
            url = base_url.format(distance + interval, distance)
            locations = session.get(url, headers=_headers).json()["results"]
            if not locations:
                break
            total += len(locations)
            logger.info(f"[{url}] +++ [total {total}] ***** {len(locations)} found")
            for _ in locations:
                page_url = locator_domain + _["url"]
                street_address = _["street_address"]
                if _["street_address2"]:
                    street_address += " " + _["street_address2"]
                if _["street_address3"]:
                    street_address += " " + _["street_address3"]
                hours = []
                for hh in _["opening_hours"]:
                    hours.append(f"{hh['name']}: {hh['label']}")
                if page_url in _urls:
                    continue
                _urls.append(page_url)
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["town"],
                    zip_postal=_["postcode"],
                    latitude=_["position"]["y"],
                    longitude=_["position"]["x"],
                    country_code="GB",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    location_type=_["location_type"],
                    hours_of_operation="; ".join(hours),
                )
            distance += interval


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
