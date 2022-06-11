from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(0, 100000, 50):
        r = session.get(
            f"https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=2500&location=68801"
            f"&limit=50&api_key=760ce2cf076e793ee9fad6f5db88c3c2&v=20181201&offset={i}"
        )
        js = r.json()["response"]["entities"]
        for j in js:
            a = j.get("address") or {}
            street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
            city = a.get("city")
            location_name = f"{j.get('name')} {city}"
            page_url = j.get("landingPageUrl")

            if location_name.lower().find(" open") != -1:
                location_name = j.get("name")

            if location_name.lower().find("closed") != -1:
                continue

            state = a.get("region")
            postal = a.get("postalCode")
            country_code = a.get("countryCode")
            phone = j.get("mainPhone")

            g = j.get("yextDisplayCoordinate") or {}
            latitude = g.get("latitude")
            longitude = g.get("longitude")

            hours = j.get("hours") or {}
            _tmp = []
            for k, v in hours.items():
                if k == "holidayHours" or k == "reopenDate":
                    continue

                day = k
                if v.get("isClosed"):
                    _tmp.append(f"{day.capitalize()}: Closed")
                    continue
                interval = v.get("openIntervals")[0]
                start = interval.get("start")
                end = interval.get("end")
                line = f"{day.capitalize()}: {start} - {end}"
                _tmp.append(line)

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 50:
            break


if __name__ == "__main__":
    locator_domain = "https://epicwingsnthings.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
