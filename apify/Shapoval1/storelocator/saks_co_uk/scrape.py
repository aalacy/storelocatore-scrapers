from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.saks.co.uk/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://bookings.saloniq.co.uk",
        "Connection": "keep-alive",
        "Referer": "https://bookings.saloniq.co.uk/main/main?url=saks.co.uk&origin=https%3A%2F%2Fwww.saks.co.uk&page=https%3A%2F%2Fwww.saks.co.uk%2Fsalons-near-you%2F%3Fbh-sl-address%3DLondon&id=1de8ec9e-4e9b-4d58-b1be-39a994532427&sid=&timestamp=1642671954407&userid=&cookieconsent=false&plr=&w=1&bh-sl-address=London",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    data = '{"tenantInfo":"{\\"url\\":\\"saks.co.uk\\",\\"origin\\":\\"https%3A%2F%2Fwww.saks.co.uk\\",\\"page\\":\\"https%3A%2F%2Fwww.saks.co.uk%2Fsalons-near-you%2F%3Fbh-sl-address%3DLondon\\",\\"tenantid\\":\\"1de8ec9e-4e9b-4d58-b1be-39a994532427\\",\\"Fid\\":\\"\\",\\"userid\\":\\"\\"}"}'

    r = session.post(
        "https://bookings.saloniq.co.uk/main/GetSalons", headers=headers, data=data
    )
    js = r.json()["Data"]["Salons"]
    for j in js:

        page_url = "https://www.saks.co.uk/salon-finder/"
        location_name = j.get("Name")
        street_address = f"{j.get('Address1')} {j.get('Address2')}".strip()
        state = "<MISSING>"
        postal = j.get("PostCode")
        country_code = "UK"
        city = j.get("Address3") or j.get("Address4") or j.get("Address2")
        if str(city).find(",") != -1:
            city = str(city).split(",")[1].strip()
        if str(street_address).find(f"{city}") != -1:
            street_address = (
                str(street_address).split(f"{city}")[0].replace(",", "").strip()
            )
        latitude = j.get("GeocodeLatitude")
        longitude = j.get("GeocodeLongitude")
        if latitude == longitude:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = j.get("PhoneNumber") or "<MISSING>"
        hours_of_operation = j.get("SalonOpeningTime")

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
            raw_address=f"{street_address} {city} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
