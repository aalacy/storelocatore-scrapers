from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def get_hours(hours) -> str:
    tmp = []
    for h in hours[7:]:
        days = h.get("day")
        opens = h.get("start_time")
        closes = h.get("end_time")
        line = f"{days} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.chilisindia.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "X-Use-Lang": "en",
        "Origin": "https://www.chilisindia.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Authorization": "apikey biz_adm_ERGHpIFWWIVEDpPXYPesoo:9178d1f0afe2ec838796b7db763629e10b7b4dde",
        "Referer": "https://www.chilisindia.com/",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    r = session.get("https://api.urbanpiper.com/api/v1/stores/", headers=headers)
    js = r.json()["stores"]
    for j in js:

        page_url = "https://www.chilisindia.com/storelocator"
        location_name = j.get("name")
        ad = j.get("address")
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            continue
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "India"
        city = a.city or j.get("city") or "<MISSING>"
        if city == "<MISSING>":
            city = str(location_name).split(",")[1].strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        if str(phone).find("/") != -1:
            phone = str(phone).split("/")[0].strip()
        hours = j.get("time_slots") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
