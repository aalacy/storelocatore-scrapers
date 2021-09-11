from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://baskinrobbinsindia.com"
base_url = "https://baskinrobbinsindia.com/locations"
city_url = "https://baskinrobbinsindia.com/getcat/locate_city/3"
json_url = "https://baskinrobbinsindia.com/getcat/getStoresbycityid/{}"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var saarcCountrys =")[1]
            .split("jQuery.each")[0]
            .strip()[:-1]
        )["countrys"]
        for country, cc in locations.items():
            for city, stores in cc["citys"].items():
                for _ in stores["stores"]:
                    addr = _["address"].split(",")
                    yield SgRecord(
                        location_name=_["name"],
                        street_address=", ".join(addr[:-2]),
                        city=addr[-2],
                        country_code=country,
                        phone=_["phonenumber"].split(",")[0],
                        locator_domain=locator_domain,
                        raw_address=_["address"],
                    )
        cities = session.get(city_url, headers=_headers).json()
        for city in cities:
            locations = session.get(
                json_url.format(city["city_id"]), headers=_headers
            ).json()
            for _ in locations:
                longitude = _["lng"]
                latitude = _["lat"]
                if not longitude:
                    _lat = latitude.split(".")
                    latitude = ".".join(_lat[:2])
                    longitude = ".".join(_lat[2:])
                yield SgRecord(
                    store_number=_["store_id"],
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city_name"],
                    state=_["state_name"],
                    country_code=_["country_name"],
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    latitude=latitude,
                    longitude=longitude,
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
