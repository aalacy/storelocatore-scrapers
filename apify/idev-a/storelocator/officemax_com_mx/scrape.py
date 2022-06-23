from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
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
            try:
                desc = _[5][1][1][0]
            except:
                continue
            raw_address = (
                desc.split("Dirección:")[-1]
                .split("\\n\\n")[0]
                .split("Teléfono")[0]
                .strip()
            )
            raw_address = " ".join([rr for rr in raw_address.split() if rr.strip()])
            if "Teléfono" in desc:
                phone = desc.split("Teléfono:")[1].split("\\n")[0].strip()
            hr = desc.split("\\n\\n")
            hours = []
            if hr[-1].startswith("Página"):
                del hr[-1]
            for hh in hr[-1].split("\\n"):
                if (
                    "Página" in hh
                    or "Dirección" in hh
                    or "Teléfono" in hh
                    or "Whatsapp" in hh
                ):
                    continue
                if not hh.strip():
                    continue
                hours.append(": ".join([_hh.strip() for _hh in hh.split()]))
            addr = raw_address.replace("\\n", "\n").strip().split("\n")
            street_address = " ".join(addr[:-2])
            if street_address.endswith(","):
                street_address = street_address[:-1]
            city = addr[-2].split(",")[0]
            state = addr[-2].split(",")[-1]
            if "Soliralidad Quintana Roo" in city:
                city = "Soliralidad"
                state = "Quintana Roo"
            if "Guadalajara Jalisco" in state:
                street_address += " " + city
                state = "Jalisco"
                city = "Guadalajara"
            if city == "Aguascalientes":
                city = ""
            if "Mexicali" in city:
                street_address += " " + city.split("Mexicali")[0].strip()
                city = "Mexicali"
            if "Puebla" in city:
                street_address += " " + city.split("Puebla")[0].strip()
                city = "Puebla"

            yield SgRecord(
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=addr[-1]
                .split(":")[-1]
                .replace("C.P.", "")
                .replace("CP.", ""),
                country_code="Mexico",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=", ".join(addr),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
