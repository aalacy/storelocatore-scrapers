from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.dare2b.com/"
base_url = "https://backend-dare2b-uk.basecamp-pwa-prod.com/api/ext/store-locations/search?lat1=52.536273191622705&lng1=-122.47558631250001&lat2=17.727758845003045&lng2=-68.95019568750001"
days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["result"]["hits"][
            "hits"
        ]
        for loc in locations:
            _ = loc["_source"]
            street_address = _["street"]
            if _["street_line_2"]:
                street_address += " " + _["street_line_2"]

            city = _["city"]
            hours = []
            hh = json.loads(_["opening_hours"])
            for day in days:
                start = hh.get(f"{day}_from")
                end = hh.get(f"{day}_to")
                if start:
                    hours.append(f"{day}: {start} - {end}")

            zip_postal = _["postcode"].strip()
            state = _["region"]
            if not state:
                if not zip_postal.split()[0].isdigit():
                    state = zip_postal.split()[0]
                    zip_postal = zip_postal.split()[-1]
            country_code = _["country"]
            if zip_postal == "n/a":
                zip_postal = ""

            raw_address = (
                f"{street_address}, {city}, {state}, {zip_postal}, {country_code}"
            )
            if "Coming Soon" in _["telephone"]:
                continue

            yield SgRecord(
                page_url="https://www.dare2b.com/store-locator/",
                store_number=_["store_id"],
                location_name=f'{_["name"]} ({_["code"]})',
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                latitude=_["location"]["lat"],
                longitude=_["location"]["lon"],
                country_code=_["country"],
                phone=_["telephone"],
                location_type=loc["_type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
