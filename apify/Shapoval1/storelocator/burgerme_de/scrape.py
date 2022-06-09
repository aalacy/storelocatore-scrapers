from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burgerme.de/"
    api_url = (
        "https://www.burgerme.de/wp-admin/admin-ajax.php?action=get_global_meta_data"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["features"]
    for j in js:

        a = j.get("properties")
        location_name = a.get("name") or "<MISSING>"
        location_type = a.get("type") or "<MISSING>"
        street_address = str(a.get("address")).strip() or "<MISSING>"
        postal = a.get("plz") or "<MISSING>"
        country_code = "DE"
        city = a.get("city") or "<MISSING>"
        store_number = a.get("id") or "<MISSING>"
        page_url = f"https://www.burgerme.de/?p={store_number}"
        latitude = (
            str(j.get("geometry").get("coordinates")[1]).replace("None", "").strip()
            or "<MISSING>"
        )
        longitude = (
            str(j.get("geometry").get("coordinates")[0]).replace("None", "").strip()
            or "<MISSING>"
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        phone = (
            " ".join(
                tree.xpath(
                    '//h2[contains(text(), "Öffnungszeiten:")]/preceding::div[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//*[contains(text(), "Montag")]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
