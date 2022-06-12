from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.7-eleven.com.hk"
base_url = "https://www.7-eleven.com.hk/en/api/store"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = parse_address_intl(_["address"] + ", China")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address == 'R/ B/K" C':
                street_address = _["address"]
            hours = []
            if _["opening_24"]:
                hours = ["24 hours"]
            else:
                hours.append(f"Monday to Friday: {_['opening_weekday']}")
                hours.append(f"Saturday: {_['opening_sat']}")
                hours.append(f"Sunday: {_['opening_sun']}")

            yield SgRecord(
                page_url="https://www.7-eleven.com.hk/en/store",
                location_name=_["district_key"],
                street_address=street_address,
                city=_["region"],
                latitude=_["latlng"].split("|")[0],
                longitude=_["latlng"].split("|")[1],
                country_code="China",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
