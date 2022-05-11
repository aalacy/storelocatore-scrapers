from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burgerking.dk"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://www.burgerking.dk",
        "Connection": "keep-alive",
        "Referer": "https://www.burgerking.dk/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
    }

    json_data = {
        "coordinates": {
            "latitude": 55.6774425609295,
            "longitude": 12.56875951826194,
        },
        "radius": 400000,
        "top": 500,
    }

    r = session.put(
        "https://bk-dk-ordering-api.azurewebsites.net/da/ordering/menu/restaurants/find",
        headers=headers,
        json=json_data,
    )
    js = r.json()["data"]["list"]
    for j in js:

        location_name = j.get("storeName") or "<MISSING>"
        ad = (
            "".join(j.get("storeAddress")).replace("\n", " ").replace("\t", " ").strip()
        )
        ad = " ".join(ad.split())
        b = parse_address(International_Parser(), ad)
        street_address = f"{b.street_address_1} {b.street_address_2}".replace(
            "None", ""
        ).strip()
        postal = b.postcode or "<MISSING>"
        if street_address.find("Kbh V") != -1:
            street_address = ad.split(f"{postal}")[0].strip()
        if street_address.find(f"{postal}") != -1:
            street_address = ad.split(f"{postal}")[0].strip()
        country_code = "DK"
        city = location_name
        if city.find("(") != -1:
            city = city.split("(")[0].strip()
        slug = j.get("slug")
        latitude = j.get("storeLocation").get("coordinates").get("latitude")
        longitude = j.get("storeLocation").get("coordinates").get("longitude")
        r = session.get(
            f"https://bk-dk-ordering-api.azurewebsites.net/da/ordering/menu/restaurants/{slug}"
        )
        js = r.json()
        phone = js.get("data").get("storeContactNumber") or "<MISSING>"
        page_url = f"https://www.burgerking.dk/restaurants/{slug}"
        hours_of_operation = "<MISSING>"
        hours = js.get("data").get("storeOpeningHours")
        tmp = []
        if hours:
            for h in hours:
                day = h.get("dayOfTheWeek")
                opens = (
                    str(h.get("hoursOfBusiness").get("opensAt"))
                    .replace(":00:00", ":00")
                    .replace(":30:00", ":30")
                    .strip()
                )
                if opens.find("T") != -1:
                    opens = opens.split("T")[1].strip()
                closes = (
                    str(h.get("hoursOfBusiness").get("closesAt"))
                    .replace(":00:00", ":00")
                    .replace(":30:00", ":30")
                    .strip()
                )
                if closes.find("T") != -1:
                    closes = closes.split("T")[1].strip()
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
