from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://www.officemax.com.mx/"
base_url = "https://www.google.com/maps/d/u/0/viewer?mid=1zg_vtoxbGRpEb5y3TAelC1XfBvAr3rCP&ll=24.69919057681412%2C-101.91799495000002&z=5"


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
            .replace("\\", "#")
            .replace("\xa0", " ")
        )
        locations = json.loads(
            cleaned.split('var _pageData = "')[1].split('";</script>')[0]
        )
        for _ in locations[1][6][0][12][0][13][0]:
            location_name = _[5][0][1][0]
            phone = ""
            latitude = _[1][0][0][0]
            longitude = _[1][0][0][1]
            desc = _[5][1][1][0]
            raw_address = (
                desc.split("Dirección:")[-1].split("##")[0].replace("#", " ").strip()
            )
            if "Teléfono" in desc:
                phone = desc.split("Teléfono:")[1].split("#")[0].strip()
            hr = desc.split("##")
            if "http" in hr[-1]:
                del hr[-1]
            if "Teléfono" in hr[-1]:
                del hr[-1]
            hours = []
            if "Dirección" not in hr[-1] and "C.P." not in hr[-1]:
                for hh in hr[-1].split("#"):
                    hours.append(": ".join([_hh.strip() for _hh in hh.split()]))
            addr = parse_address_intl(raw_address + ", Mexico")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            yield SgRecord(
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Mexico",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
