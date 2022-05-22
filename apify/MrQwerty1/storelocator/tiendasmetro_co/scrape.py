import json5
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://metrocolombiaio.vtexassets.com/_v/public/assets/v1/published/tiendasjumboqaio.metro-custom-pages@2.0.0/public/react/StoreLocator.min.js"
    r = session.get(api, headers=headers)
    text = r.text
    text = "[{name" + text.split("[{name")[1].split("}]}]")[0] + "}]}]"
    js = json5.loads(text)

    for s in js:
        city = s.get("name")
        jj = s.get("offices") or []

        for j in jj:
            street_address = j.get("address")
            country_code = "CO"
            location_name = j.get("name")
            phone = j.get("phone") or ""
            if "Domicilios" in phone:
                phone = phone.split("Domicilios")[0].strip()
            phone = phone.replace("-", " ").strip()
            latitude = j.get("lat")
            longitude = j.get("lng")
            hours = j.get("schedule") or []
            hours_of_operation = ";".join(hours).replace(" - ", ";")

            black = [";Domingos", ";Fines", ";Los"]
            for b in black:
                if b in hours_of_operation:
                    hours_of_operation = hours_of_operation.split(b)[0].strip()

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.tiendasmetro.co/"
    page_url = "https://www.tiendasmetro.co/institucional/nuestras-tiendas"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
