from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgscrape.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://dottys.com/"
base_url = "https://dottys.com/"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


def fetch_data():
    streets = []
    with SgRequests() as session:
        urls = bs(session.get(base_url, headers=_headers()).text, "lxml").select(
            "a.location"
        )
        for url in urls:
            res = session.get(url["href"], headers=_headers())
            locations = json.loads(
                res.text.split('var _pageData = "')[1]
                .split('";</script>')[0]
                .replace("null", '"null"')
                .replace("\xa0", "")
                .replace('\\"', '"')
                .strip()
            )[1][6][0][12][0][13][0]
            for _ in locations:
                location_name = _[5][0][1][0].replace("\\u0026", "&").strip()
                if not location_name.startswith("Dotty"):
                    continue
                addr = parse_address_intl(
                    _[5][1][1][0].replace("\\u0026", "&").replace("\\n", "").strip()
                )
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2
                if street_address in streets:
                    continue
                streets.append(street_address)
                yield SgRecord(
                    location_name=location_name,
                    street_address=street_address,
                    city=addr.city,
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="US",
                    latitude=_[1][0][0][0],
                    longitude=_[1][0][0][1],
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
