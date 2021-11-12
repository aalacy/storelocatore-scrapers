from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://burgerkingbangladesh.com/"
    api_url = "https://burgerkingbangladesh.com/delivery"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//option[text()="PLEASE ENTER DELIVERY LOCATION"]/following-sibling::option'
    )
    for d in div:
        ids = "".join(d.xpath(".//@value"))

        session = SgRequests()
        r = session.get(
            f"https://burgerkingbangladesh.com/bkashmicrosite/locationwisebranch?locationid={ids}",
            headers=headers,
        )
        js = r.json()
        if js is None:
            continue

        page_url = "https://burgerkingbangladesh.com/delivery"
        location_name = js.get("branchname")
        street_address = js.get("address") or "<MISSING>"
        country_code = "Bangladesh"
        latitude = js.get("latitude") or "<MISSING>"
        longitude = js.get("longitude") or "<MISSING>"
        phone = js.get("contactno") or "<MISSING>"
        hours_of_operation = (
            f"Monday {js.get('monday')} Tuesday {js.get('tuesday')} Wednesday {js.get('wednesday')} Thursday {js.get('thursday')} Friday {js.get('friday')} Saturday {js.get('saturday')} Sunday {js.get('sunday')}"
            or "<MISSING>"
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=SgRecord.MISSING,
            state=SgRecord.MISSING,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
