from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import dirtyjson as json
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


locator_domain = "https://kentucky.com.do/"
base_url = "https://www.google.com/maps/d/u/0/embed?mid=1OfbjXtapo3bVX8fvMQjZWepApdU&ll=18.944487881378887%2C-70.13776369946288&z=7"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _p(val):
    return (
        val.split(":")[-1]
        .replace("\\n", "")
        .replace("Teléfono", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def _d(_):
    location_name = _[5][0][1][0].replace("\\n", "").replace("\n", "")
    _blocks = [bb for bb in _[5][1][1][0].split("\\n\\n") if bb.strip()]
    blocks = []
    blocks += _blocks[0].split(" \\n")
    for bb in _blocks[1:]:
        blocks.append(bb)
    phone = ""
    if "Coord" in blocks[1]:
        del blocks[1]
    if _p(blocks[-1]):
        phone = (
            blocks[-1].split(":")[-1].replace("Teléfono", "").replace("\\n", "").strip()
        )
        del blocks[-1]
    latitude = _[1][0][0][0]
    longitude = _[1][0][0][1]
    addr = parse_address_intl(" ".join(blocks[:-1]) + ", Dominican Republic")
    street_address = addr.street_address_1 or ""
    if addr.street_address_2:
        street_address += ", " + addr.street_address_2
    hours_of_operation = ""
    if len(blocks) > 1:
        hours_of_operation = (
            blocks[-1].replace("\\n", "").replace("Horarios:", "").replace("/", ";")
        )
    return SgRecord(
        location_name=location_name,
        street_address=street_address,
        city=addr.city,
        state=addr.state,
        zip_postal=addr.postcode,
        country_code="Dominican Republic",
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        raw_address=blocks[0],
        hours_of_operation=hours_of_operation,
    )


def fetch_data():
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers)
        cleaned = (
            res.text.replace('\\"', '"')
            .replace("\\\\u003d", "=")
            .replace("\\\\u0026", "&")
        )
        locations = json.loads(
            cleaned.split('var _pageData = "')[1].split('";</script>')[0]
        )
        for _ in locations[1][6][0][12][0][13][0]:
            yield _d(_)

        for _ in locations[1][6][1][12][0][13][0]:
            yield _d(_)

        for _ in locations[1][6][2][12][0][13][0]:
            yield _d(_)

        for _ in locations[1][6][3][12][0][13][0]:
            yield _d(_)

        for _ in locations[1][6][4][12][0][13][0]:
            yield _d(_)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
