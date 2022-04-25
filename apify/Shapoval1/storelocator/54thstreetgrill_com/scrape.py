from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours):
    tmp = []
    for h in hours:
        days = h.get("weekDay")
        times = h.get("description")
        line = f"{days} {times}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.54thstreetgrill.com"
    api_url = "https://order.54expresstogo.com/api/vendors/regions?excludeCities=true"
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
        "Referer": "https://order.54expresstogo.com/locations",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        slug = j.get("code")

        session = SgRequests()
        r = session.get(
            f"https://order.54expresstogo.com/api/vendors/search/{slug}",
            headers=headers,
        )
        js = r.json()["vendor-search-results"]
        for j in js:

            slug = j.get("slug")
            page_url = f"https://order.54expresstogo.com/menu/{slug}"
            location_name = j.get("name")
            street_address = j.get("streetAddress")
            state = j.get("state")
            postal = "<MISSING>"
            country_code = "US"
            city = j.get("city")
            phone = j.get("phoneNumber")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            hours = j.get("weeklySchedule").get("calendars")[1].get("schedule")
            hours_of_operation = get_hours(hours)

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
