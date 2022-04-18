from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


locator_domain = "https://www.regatta.com/"
base_url = "https://backend-regatta-uk.basecamp-pwa-prod.com/api/ext/store-locations/search?lat1=52.536273191622705&lng1=-122.51953162500001&lat2=17.727758845003045&lng2=-68.90625037500001"

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["result"]["hits"][
            "hits"
        ]
        for loc in locations:
            _ = loc["_source"]
            if 'Coming Soon' in _['telephone']:
                continue
            street_address = _["street"]
            if _["street_line_2"]:
                street_address += " " + _["street_line_2"]

            hours = []
            hh = json.loads(_["opening_hours"])
            for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                day = day.lower()
                start = hh.get(f"{day}_from")
                end = hh.get(f"{day}_to")
                hours.append(f"{day}: {start} - {end}")

            raw_address = f"{street_address} {_['city']} {_['region']} {_['postcode']} {_['country']}".replace(
                ",", ""
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url="https://www.regatta.com/us/store-locator/",
                store_number=_["store_id"],
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["location"]["lat"],
                longitude=_["location"]["lon"],
                country_code=_["country"],
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.PHONE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
