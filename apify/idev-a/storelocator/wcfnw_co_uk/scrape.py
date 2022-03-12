from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://www.wcfnw.co.uk"
base_url = "https://www.google.com/maps/d/embed?mid=1EWYElqRIGsM6DDnU4BfuYOKjs2_sqo1V"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers())
        cleaned = (
            res.text.replace("\\\\u003d", "=")
            .replace("\\\\u0026", "&")
            .replace('\\"', '"')
            .replace("\\n", "")
            .replace("\xa0", " ")
        )
        locations = json.loads(
            cleaned.split('var _pageData = "')[1].split('";</script>')[0]
        )
        for _ in locations[1][6][0][12][0][13][0]:
            location_name = _[5][0][1][0]
            latitude = _[1][0][0][0]
            longitude = _[1][0][0][1]
            raw_address = _[5][1][1][0]
            street_address = city = state = zip_postal = ""
            if len(raw_address.split()) > 2:
                addr = parse_address_intl(raw_address + ", United Kingdom")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2
                city = addr.city
                state = addr.state
                zip_postal = addr.postcode
            else:
                zip_postal = raw_address
                city = location_name.replace("Depot", "").replace("Deport", "").strip()
            yield SgRecord(
                page_url="https://www.wcfnw.co.uk/find-your-local-depot",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="UK",
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
