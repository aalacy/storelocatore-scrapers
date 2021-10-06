import datetime
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        dayss = "".join(h.get("date"))
        year = int(dayss.split("-")[0])
        month = int(dayss.split("-")[1])
        days = int(dayss.split("-")[2])
        ans = datetime.date(year, month, days)
        day = ans.strftime("%A")
        opens = "".join(h.get("onTime")).split()[1]
        closes = "".join(h.get("offTime")).split()[1]
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    return "; ".join(tmp)


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.hardees.com.kw/"
    api_url = "https://www.hardees.com.kw/api/stores?deliveryMode=H&langCode=en"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["body"]
    for j in js:

        page_url = "https://www.hardees.com.kw/en/search-location"
        location_name = j.get("name") or "<MISSING>"
        street_address = (
            "".join(j.get("address")).replace("\r\n", "").strip() or "<MISSING>"
        )
        state = j.get("state").get("name") or "<MISSING>"
        country_code = j.get("country").get("code") or "<MISSING>"
        city = j.get("city").get("name") or "<MISSING>"
        latitude = j.get("locationDetail").get("latitude") or "<MISSING>"
        longitude = j.get("locationDetail").get("longitude") or "<MISSING>"
        hours = j.get("storeTimings").get("HomeDelivery")
        phone = j.get("contactNo") or "<MISSING>"
        hours_of_operation = get_hours(hours)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
