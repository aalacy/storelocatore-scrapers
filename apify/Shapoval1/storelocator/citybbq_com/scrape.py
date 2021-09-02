from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("weekDay")
        time = h.get("description")
        line = f"{day} {time}"
        tmp.append(line)
    hours_of_operation = ";".join(tmp) or "<MISISNG>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.citybbq.com/"
    api_url = "https://citybbq.olo.com/api/vendors/regions?excludeCities=true"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "__RequestVerificationToken": "",
        "X-Requested-With": "XMLHttpRequest",
        "X-Olo-Request": "1",
        "X-Olo-Viewport": "Desktop",
        "X-Olo-App-Platform": "web",
        "Connection": "keep-alive",
        "Referer": "https://citybbq.olo.com/locations",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        code = j.get("code")
        session = SgRequests()
        r = session.get(
            f"https://citybbq.olo.com/api/vendors/search/{code}", headers=headers
        )
        js = r.json()["vendor-search-results"]
        for j in js:
            page_url = f"https://citybbq.olo.com/menu/{j.get('slug')}"
            location_name = j.get("name")
            street_address = f"{j.get('address').get('streetAddress')} {j.get('address').get('streetAddress2')}".strip()
            state = j.get("state")
            postal = j.get("address").get("postalCode")
            country_code = "US"
            city = j.get("city")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            phone = j.get("phoneNumber")
            hours_of_operation = "<MISSING>"
            try:
                hours = (
                    j.get("weeklySchedule").get("calendars")[0].get("schedule")
                    or "<MISSING>"
                )
            except:
                hours = "<MISSING>"
            if hours != "<MISSING>":
                hours_of_operation = str(get_hours(hours))

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
