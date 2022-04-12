from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    for i in range(1, 100):
        api = f"https://api.woosmap.com/stores/search?key=woos-6256d36f-af9b-3b64-a84f-22b2342121ba&lat=48.856697&lng=2.3514616&stores_by_page=300&page={i}&query=user.type:=%22pdv%22%20AND%20(user.commercialActivity.activityCode:=%22101%22%20OR%20user.commercialActivity.activityCode:=%22102%22)"
        country_code = "FR"
        r = session.get(api, headers=headers)
        js = r.json()["features"]

        for j in js:
            p = j.get("properties") or {}
            up = p.get("user_properties") or {}
            g = j.get("geometry") or {}
            a = p.get("address") or {}

            store_number = p.get("store_id")
            location_name = p.get("name")
            try:
                phone = p["contact"]["phone"]
            except:
                phone = SgRecord.MISSING

            page_url = up.get("urlStore")
            lines = a.get("lines") or []
            street_address = " ".join(lines)
            city = a.get("city")
            postal = a.get("zipcode")
            longitude, latitude = g.get("coordinates") or [
                SgRecord.MISSING,
                SgRecord.MISSING,
            ]

            _tmp = []
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            try:
                hours = p["opening_hours"]["usual"]
            except KeyError:
                hours = dict()

            for k, v in hours.items():
                index = int(k) - 1
                day = days[index]
                if not v:
                    continue
                try:
                    start = v[0]["start"]
                    end = v[0]["end"]
                except:
                    continue
                _tmp.append(f"{day}: {start}-{end}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                phone=phone,
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 300:
            break


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "e.leclerc"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
        "Referer": f"https://www.{locator_domain}/",
        "Origin": f"https://www.{locator_domain}",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Connection": "keep-alive",
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
