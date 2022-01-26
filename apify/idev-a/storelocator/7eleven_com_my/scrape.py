from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://7eleven.com.my"
base_url = "https://www.google.com/maps/d/u/0/viewer?mid=1Dcxo7WR64emFqXx_aivDDMVcdH8&ll=3.1005461000000047%2C101.60534700000002&z=8"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


def _phone(val):
    return (
        val.replace("Phone", "")
        .replace("-", "")
        .replace(")", "")
        .replace("(", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers())
        cleaned = (
            res.text.replace("\\t", " ")
            .replace("\\\\u003d", "=")
            .replace("\\\\u0026", "&")
            .replace("\xa0", " ")
            .replace('\\"', '"')
        )
        locations = json.loads(
            cleaned.split('var _pageData = "')[1].split('";</script>')[0]
        )
        for _ in locations[1][6][0][12][0][13][0]:
            location_name = _[5][0][1][0]
            latitude = _[1][0][0][0]
            longitude = _[1][0][0][1]
            raw_address = _[5][3][1][1][0].replace("\\n", " ").strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            yield SgRecord(
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Malaysia",
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
