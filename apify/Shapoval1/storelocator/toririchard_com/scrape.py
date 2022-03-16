from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://toririchard.com/"
    api_url = "https://cdn.shopify.com/s/files/1/0265/8762/7586/t/89/assets/sca.storelocator_scripttag.js?v=1642029367&shop=toririchard-com.myshopify.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    jsblock = (
        r.text.split('"locationsRaw":"')[1]
        .split('","app_url"')[0]
        .replace("\\", "")
        .strip()
    )
    js = eval(jsblock)
    for j in js:

        page_url = "https://toririchard.com/pages/store-locator"
        location_name = "".join(j.get("name")) or "<MISSING>"
        if location_name.find("Kuku") != -1:
            location_name = location_name.replace("Kukuiâ€™ula", "Kukui’ula").strip()
        street_address = j.get("address")
        street_address2 = j.get("address2") or "<MISSING>"
        if (
            "Unit" in street_address2
            or "Suite" in street_address2
            or "#" in street_address2
        ):
            street_address = street_address + " " + street_address2
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = (
            "".join(j.get("schedule"))
            .replace("\\r", "")
            .replace("<br>", " ")
            .replace("\\", "")
            .replace("Open", "")
            .replace("r ", " ")
            .strip()
            .strip()
            or "<MISSING>"
        )

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
