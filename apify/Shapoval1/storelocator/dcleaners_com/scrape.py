from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.dcleaners.com/"
    api_url = "https://www.dcleaners.com/wp-json/acf/v3/dc-locations?per_page=5000"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        a = j.get("acf")
        ad = a.get("location_address")
        location_name = a.get("location_name") or "<MISSING>"
        street_address = (
            f"{ad.get('location_address_1')} {ad.get('location_address_2')}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        state = ad.get("location_state") or "<MISSING>"
        postal = ad.get("location_zip") or "<MISSING>"
        country_code = "US"
        city = ad.get("location_city") or "<MISSING>"
        store_number = j.get("id")
        latitude = a.get("google_map").get("lat")
        longitude = a.get("google_map").get("lng")
        phone = a.get("location_phone") or "<MISSING>"
        if str(phone).find("x22") != -1:
            phone = str(phone).replace("x22", "").strip()
        hours = a.get("hours_of_operation")
        hours_of_operation = "<MISSING>"
        if hours:
            b = html.fromstring(hours)
            hours_of_operation = (
                " ".join(b.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("temporarily closed") != -1:
            hours_of_operation = "Temporarily closed"
        r = session.get(
            "https://www.dcleaners.com/wp-json/dclocation/v3/get-location-permalink"
        )
        js = r.json()
        page_url = js.get(f"{store_number}").get("slug")

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
