from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://sparhellas.com/"
    api_url = "https://sparhellas.com/wp-admin/admin-ajax.php?lang=en&action=store_search&lat=37.98381&lng=23.72754&max_results=50&search_radius=900&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://sparhellas.com/en/stores-en/"
        location_name = "".join(j.get("store")).replace("&#8211;", "-") or "<MISSING>"
        street_address = (
            f"{j.get('address')} {' '.join(''.join(j.get('address2')).split(',')[:-1])}".strip()
            or "<MISSING>"
        )
        if street_address.find(", Τηλ") != -1:
            street_address = street_address.split(", Τηλ.")[0].strip()
        state = "".join(j.get("state")) or "<MISSING>"
        if state == "-":
            state = "<MISSING>"
        postal = "".join(j.get("zip")) or "<MISSING>"
        if postal.find("-") != -1:
            postal = postal.replace("-", "").strip()
        country_code = "Greece"
        city = "".join(j.get("city")).replace("-", "").strip() or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = "".join(j.get("phone")) or "<MISSING>"
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()
        hours = j.get("hours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
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
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
