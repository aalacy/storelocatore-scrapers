from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://support-ca.samsung.com/seca/api/stores/get?api_key=55a75e7599d56ed685ebc035d642b38aa9ce4507&language=en"
    page_url = "https://www.samsung.com/ca/ses/"
    r = session.get(api, headers=headers)
    js = r.json()["data"]

    for j in js:
        location_name = j.get("name")
        street_address = f'{j.get("address1")} {j.get("address2") or ""}'.strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zipcode")
        phone = j.get("phone")
        store_number = j.get("store_id")
        text = j.get("directions") or ""
        try:
            if "ll=" in text:
                latitude, longitude = text.split("ll=")[1].split("&")[0].split(",")
            else:
                latitude, longitude = text.split("@")[1].split(",")[:2]
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

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
        h = j.get("hours") or {}
        for day in days:
            key = day[:3].lower()
            start = h.get(f"{key}_start")
            end = h.get(f"{key}_end")
            _tmp.append(f"{day}: {start}-{end}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="CA",
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.samsung.com/ca/ses/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
