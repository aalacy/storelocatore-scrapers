from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING

    return street, city


def fetch_data(sgw: SgWriter):
    api = "https://z.co.nz/locator-api/v1/allstations"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        raw_address = j.get("address")
        street_address, city = get_international(raw_address)
        state = j.get("region")
        country_code = "NZ"
        store_number = j.get("id")
        location_name = j.get("name")
        slug = j.get("link")
        page_url = f"https://z.co.nz{slug}"
        location_type = j.get("type")
        phone = j.get("phone") or ""
        if phone:
            if "Ph" in phone:
                phone = phone.split("Ph")[-1].replace(":", "").strip()
            if phone[0].isalpha() and phone[-1].isalpha():
                phone = SgRecord.MISSING
        latitude = j.get("lat")
        longitude = j.get("lng")

        if j.get("isOpenTwentyFourSeven"):
            hours_of_operation = "Open 24 hours"
        else:
            _tmp = []
            hours = j.get("hours") or []
            for h in hours:
                day = h.get("day")
                inter = h.get("hours")
                if inter:
                    _tmp.append(f"{day}: {inter}")

            hours_of_operation = ";".join(_tmp) or "Closed"
            if hours_of_operation.count("Open 24 hours") == 7:
                hours_of_operation = "Open 24 hours"
            if hours_of_operation.count("Closed") > 7:
                hours_of_operation = "Closed"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code=country_code,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://z.co.nz/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
