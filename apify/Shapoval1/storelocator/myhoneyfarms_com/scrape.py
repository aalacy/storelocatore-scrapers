from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://myhoneyfarms.com/locations/"
    api_url = "https://myhoneyfarms.com/wp-admin/admin-ajax.php?action=store_search&lat=40.75369&lng=-73.99916&max_results=100&search_radius=1000"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country") or "US"
        store_number = j.get("id")
        page_url = j.get("permalink")
        location_name = "".join(j.get("store")).replace("&#8211;", "-")
        phone = j.get("phone")
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        text = j.get("hours")
        a = html.fromstring(text)
        hours_of_operation = " ".join(a.xpath("//*//text()")) or "<MISSING>"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
