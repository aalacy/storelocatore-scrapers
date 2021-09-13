from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.medicalpharmacies.com/"
    api_url = "https://www.medicalpharmacies.com/wp-admin/admin-ajax.php?action=store_search&lat=48.40794&lng=-89.252564&max_results=500&search_radius=50000&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        page_url = "https://www.medicalpharmacies.com/about/locations/"
        location_name = j.get("store")
        street_address = j.get("address")
        phone = "".join(j.get("phone")) or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = "CA"
        city = "".join(j.get("city")).replace(",", "").strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = j.get("hours") or "<MISSING>"
        if hours_of_operation != "<MISSING>":
            h = html.fromstring(hours_of_operation)
            hours_of_operation = (
                " ".join(h.xpath("//*//text()")).replace("\n", "").strip()
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
            SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
