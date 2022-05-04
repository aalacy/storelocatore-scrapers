from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.velvettaco.com/"
    api_url = "https://www.velvettaco.com/wp-json/wp/v2/location?per_page=50"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        a = j.get("acf")
        page_url = j.get("link") or "<MISSING>"
        location_name = (
            str(j.get("title").get("rendered"))
            .replace("&#8211;", "–")
            .replace("&#038;", "&")
            .strip()
            or "<MISSING>"
        )
        location_type = j.get("type") or "<MISSING>"
        street_address = a.get("address") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        phone = a.get("contact").get("phone_number") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = a.get("hours_of_operation")
        tmp = []
        if hours:
            for h in hours:
                day = h.get("day")
                opens = h.get("open")
                closes = h.get("close")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        cms = a.get("coming_soon")
        if cms:
            location_type = "Coming Soon"

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
