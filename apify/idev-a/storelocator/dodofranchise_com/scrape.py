from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://dodofranchise.com/"
base_url = "https://www.google.com/maps/d/embed?ll=55.501929789497915%2C53.82075624999993&z=4&mid=1YmPD9on_m9C2cs_2n95N8GvwEo0"


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
            .replace('\\\\"', "'")
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
            raw_address = _[5][3][1][1][0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            yield SgRecord(
                page_url=locator_domain,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                latitude=latitude,
                longitude=longitude,
                location_type=_[5][3][0][1][0],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
