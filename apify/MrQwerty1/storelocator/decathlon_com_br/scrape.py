from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode or ""

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://www.decathlon.com.br/api/dataentities/SL/search"
    r = session.get(api, headers=headers, params=params)
    js = r.json()

    for j in js:
        location_name = j.get("name")
        slug = j.get("pageLink")
        page_url = f"https://www.decathlon.com.br{slug}"
        raw_address = j.get("address")
        street_address, city, state, postal = get_international(raw_address)
        if street_address == "3400":
            street_address = ",".join(raw_address.split(",")[:2])
        if "CEP" in postal:
            postal = postal.replace("CEP", "").strip()

        phone = j.get("phone")
        latitude = j.get("latitude") or ""
        longitude = j.get("longitude") or ""
        if str(longitude) == "-400":
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        if "." not in str(latitude) and latitude != SgRecord.MISSING:
            latitude = str(latitude)[:2] + "." + str(latitude)[2:]
        if "." not in str(longitude) and longitude != SgRecord.MISSING:
            longitude = str(longitude)[:2] + "." + str(longitude)[2:]
        hours = j.get("openingHours") or ""
        hours_of_operation = hours.replace("\r\n", ";").replace(";;", ";")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="BR",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.decathlon.com.br/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "application/vnd.vtex.ds.v10+json",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "REST-Range": "resources=0-1500",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.decathlon.com.br/lojas",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    params = (
        ("_where", "(status_active=true)"),
        (
            "_fields",
            "address,name,phone,openingHours,latitude,longitude,state,specialHolidaySchedule,pageLink,isStoreOpen,flag_status",
        ),
    )

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
