from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://www.egypt.kfc.me"
base_url = "https://www.google.com/maps/d/u/1/embed?mid=1Z0bXRTjU96kisUhXa5eHwO6s4g0"


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
            .replace("\\u0027", "'")
            .replace('\\\\"', "'")
            .replace('\\"', '"')
            .replace("\xa0", " ")
        )
        locations = json.loads(
            cleaned.split('var _pageData = "')[1].split('";</script>')[0]
        )
        for _ in locations[1][6][0][12][0][13][0]:
            location_name = _[5][0][1][0].replace("\\n", "")
            phone = ""
            if "Contact No" in _[5][3][-2][0]:
                phone = _[5][3][-2][1][0].split(":")[-1].replace("\\n", "").strip()
            latitude = _[1][0][0][0]
            longitude = _[1][0][0][1]
            hours = []
            if _[5][3][1][0] == "Timing":
                hours = _[5][3][1][1]
            raw_address = _[5][3][-1][1][0] + ", egypt"
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            city = addr.city
            if not city:
                city = location_name.split("-")[-1].split("(")[0].split("/")[0].strip()
            yield SgRecord(
                location_name=location_name,
                street_address=street_address.replace("egypt", ""),
                city=city,
                zip_postal=addr.postcode,
                country_code="Egypt",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("\\n", " ").strip(),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
