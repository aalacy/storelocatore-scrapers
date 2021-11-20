from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("dayOfTheWeek")
        opens = "".join(h.get("hoursOfBusiness").get("opensAt")).split("T")[1].strip()
        closes = "".join(h.get("hoursOfBusiness").get("closesAt")).split("T")[1].strip()
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burgerking.dk"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "Origin": "https://www.burgerking.dk",
        "Connection": "keep-alive",
        "Referer": "https://www.burgerking.dk/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
    }
    data = '{"coordinates":{"latitude":55.6774425609295,"longitude":12.56875951826194},"radius":400000}'

    r = session.put(
        "https://bk-dk-ordering-api.azurewebsites.net/da/ordering/menu/restaurants/find",
        headers=headers,
        data=data,
    )
    js = r.json()["data"]["list"]
    for j in js:
        slug = j.get("slug")
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
        }
        r = session.get(
            f"https://bk-dk-ordering-api.azurewebsites.net/cms/da/restaurants/{slug}",
            headers=headers,
        )
        js = r.json()["data"]

        page_url = f"https://www.burgerking.dk/restaurants/{slug}"
        location_name = js.get("storeName") or "<MISSING>"
        a = js.get("storeLocation").get("address")
        ad = (
            "".join(js.get("storeAddress"))
            .replace("\n", " ")
            .replace("\t", " ")
            .strip()
        )
        ad = " ".join(ad.split())
        b = parse_address(International_Parser(), ad)
        street_address = f"{b.street_address_1} {b.street_address_2}".replace(
            "None", ""
        ).strip()

        state = a.get("state") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        if street_address.find("Kbh V") != -1:
            street_address = ad.split(f"{postal}")[0].strip()
        if street_address.find(f"{postal}") != -1:
            street_address = ad.split(f"{postal}")[0].strip()
        country_code = "DK"
        city = a.get("city") or "<MISSING>"
        try:
            store_number = "".join(js.get("storeSubHeader")).split("#:")[1].strip()
        except:
            store_number = "<MISSING>"
        latitude = js.get("coordinates").get("latitude") or "<MISSING>"
        longitude = js.get("coordinates").get("longitude") or "<MISSING>"
        phone = js.get("storeContactNumber") or "<MISSING>"
        hours = js.get("storeOpeningHours") or "<MISSING>"
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
            store_number=store_number,
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
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
