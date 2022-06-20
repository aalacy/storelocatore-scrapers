from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(777):
        api = f"https://www.tchibo.de/service/storefinder/api/storefinder/api/stores?page={i}&size=1000"
        r = session.get(api, headers=headers)
        js = r.json()["content"]

        for j in js:
            a = j.get("addressDto") or {}
            street_address = a.get("street")
            city = a.get("city")
            postal = a.get("zip")
            country_code = a.get("country")
            store_number = j.get("id")
            location_type = j.get("storeType")
            if location_type == "Depot":
                continue
            if location_type == "Percent":
                location_name = "Tchibo Prozente"
            else:
                location_name = "Tchibo Filiale"

            if j.get("featuresCoffeeBar"):
                location_name += " mit Kaffee Bar"
            page_url = f"https://www.tchibo.de/service/storefinder/store/{store_number}"
            phone = j.get("telephoneNumber")

            g = j.get("locationGeographicDto") or {}
            latitude = g.get("lat")
            longitude = g.get("lng")

            _tmp = []
            hours = j.get("daysDto") or {}
            for day, h in hours.items():
                start = h.get("morningOpening")
                end = h.get("afternoonClosing")
                if start != "null":
                    _tmp.append(f"{day.capitalize()}: {start}-{end}")
                else:
                    _tmp.append(f"{day.capitalize()}: Closed")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                location_type=location_type,
                phone=phone,
                store_number=store_number,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)

        if len(js) < 1000:
            break


if __name__ == "__main__":
    locator_domain = "https://www.tchibo.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
