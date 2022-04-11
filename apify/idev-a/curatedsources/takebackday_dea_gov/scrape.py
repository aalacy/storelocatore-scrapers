from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://findtreatment.samhsa.gov",
    "referer": "https://findtreatment.samhsa.gov/locator",
    "x-requested-with": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dea.gov"
base_url = "https://findtreatment.samhsa.gov/locator/listing"


def fetch_data():
    page = 1
    with SgRequests() as session:
        while True:
            data = {
                "sType": "SA",
                "sAddr": "19.639994,-155.9969261",
                "pageSize": "100",
                "page": page,
                "sort": "0",
            }
            locations = session.post(base_url, headers=_headers, data=data).json()[
                "rows"
            ]
            if not locations:
                break
            page += 1
            logger.info(f"page {page} {len(locations)}")
            for _ in locations:
                street_address = _["street1"]
                if _["street2"]:
                    street_address += " " + _["street2"]
                phone = _["phone"]
                if phone:
                    phone = phone.split("x")[0]
                page_url = _["website"]
                if page_url == "http://" or page_url == "https://":
                    page_url = ""
                yield SgRecord(
                    page_url=page_url,
                    location_name="Drug Disposal Site at "
                    + (_["name1"] + " " + _.get("name2")).upper().strip(),
                    street_address=street_address,
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
