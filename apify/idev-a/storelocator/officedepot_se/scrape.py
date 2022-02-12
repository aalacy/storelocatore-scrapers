from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.officedepot.se"
base_url = "https://www.officedepot.se/vara-butiker"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).text.split("GMAPS_POINTS")[
            2:
        ]
        for x, loc in enumerate(locations):
            try:
                _ = json.loads(loc.split("=")[1].split(";")[0].strip())
            except:
                break
            raw_address = _[8]
            addr = raw_address.split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=_[4],
                street_address=", ".join(addr[:-1]),
                city=" ".join(addr[-1].strip().split()[1:]),
                zip_postal=addr[-1].strip().split()[0],
                country_code="Sweden",
                phone=_[9],
                latitude=_[0],
                longitude=_[1],
                locator_domain=locator_domain,
                hours_of_operation=_[7],
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
