from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("harvester")

base_url = "https://www.harvester.co.uk/cborms/pub/brands/9/outlets"
locator_domain = "https://www.harvester.co.uk"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    with SgRequests(verify_ssl=False) as http:
        locations = http.get(base_url, headers=_headers).json()
        logger.info(f"{len(locations)} found")
        for _ in locations:
            addr = _["address"]
            street_address = addr["line1"]
            if addr.get("line2"):
                street_address += " " + addr["line1"]

            hours = []
            url = f"https://www.harvester.co.uk/cborms/pub/brands/9/outlets/{_['bunCode']}"
            logger.info(url)
            _d = http.get(url, headers=_headers).json()
            if _d.get("outletStructure", {}):
                page_url = locator_domain + _d.get("outletStructure", {}).get("uri")
            else:
                page_url = "https://www.harvester.co.uk/restaurants#/"
            for hh in _d.get("foodServiceTimes", {}).get("periods", []):
                times = []
                for hr in hh["times"]:
                    times.append(hr["text"])
                hours.append(f"{hh['days']['text']}: {', '.join(times)}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["bunCode"],
                location_name=_["name"],
                street_address=street_address,
                city=addr["town"],
                state=addr.get("county"),
                zip_postal=addr["postcode"],
                country_code="UK",
                phone=_["telephoneNumber"],
                locator_domain=locator_domain,
                location_type=_["status"],
                latitude=_["gpsCoordinates"]["latitude"],
                longitude=_["gpsCoordinates"]["longitude"],
                hours_of_operation="; ".join(hours),
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
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
