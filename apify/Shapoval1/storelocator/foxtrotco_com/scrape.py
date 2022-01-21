from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    for h in hours:
        day = h.get("day_of_week")
        opens = h.get("opening_time")
        close = h.get("closing_time")
        line = f"{days[day]} : {opens} - {close}"
        tmp.append(line)
    hours_of_operation = " ; ".join(tmp) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://foxtrotco.com"
    ll = [1, 2, 3]
    for i in ll:
        api_url = f"https://api.foxtrotchicago.com/v5/retail-stores/?region_id={i}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "Trailers",
        }

        r = session.get(api_url, headers=headers)
        js = r.json()["stores"]
        for j in js:
            street_address = j.get("address") or "<MISSING>"
            city = j.get("city") or "<MISSING>"
            postal = j.get("zip") or "<MISSING>"
            state = "".join(j.get("state")) or "<MISSING>"
            country_code = "US"
            location_name = "".join(j.get("name")) or "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("lat") or "<MISSING>"
            slug = location_name.replace(" ", "-").lower()
            page_url = f"https://foxtrotco.com/stores/{slug}"
            longitude = j.get("lon") or "<MISSING>"
            hours = j.get("operating_hours")
            hours_of_operation = get_hours(hours)
            a_url = "".join(j.get("asset_url"))
            if "ComingSoon" in a_url or "coming-soon" in a_url:
                hours_of_operation = "Coming Soon"

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
                raw_address=f"{street_address} {city}, {state} {postal}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
