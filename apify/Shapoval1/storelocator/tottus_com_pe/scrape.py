from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.tottus.com.pe"
    api_url = "https://www.tottus.com.pe/api/contact-points?perPage=500"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["results"]
    for j in js:
        a = j.get("address")
        page_url = "https://www.tottus.com.pe/tiendas-cercanas"
        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("type") or "<MISSING>"
        if location_type != "store":
            continue
        street_address = (
            f"{a.get('streetNumber')} {a.get('streetName')}".strip() or "<MISSING>"
        )
        state = a.get("region") or "<MISSING>"
        postal = a.get("postal_code") or "<MISSING>"
        country_code = a.get("country") or "<MISSING>"
        city = a.get("district") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        ll = "".join(a.get("geoCode"))
        try:
            latitude = ll.split(",")[0].strip()
            longitude = ll.split(",")[1].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = j.get("contactInfo").get("phone") or "<MISSING>"
        if str(phone).find("/") != -1:
            phone = str(phone).split("/")[0].strip()
        hours_of_operation = "<MISSING>"
        hours = j.get("timetables")
        tmp = []
        if hours:
            for h in hours:
                day = h.get("dayOfWeek")
                opens = h.get("openHour")
                closes = h.get("closeHour")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
