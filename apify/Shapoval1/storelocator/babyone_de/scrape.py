import json
import gzip
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.babyone.de/"
    api_url = "https://www.babyone.de/sitemap/salesChannel-da7d92ba4f334915adb21b7901136f5a-2fbb5fe2e29a4d70aa5854ce7ce3e20b/da7d92ba4f334915adb21b7901136f5a-sitemap-www-babyone-de-1.xml.gz"
    session = SgRequests(verify_ssl=False)
    r = session.get(api_url)
    tree = html.fromstring(gzip.decompress(r.content))
    div = tree.xpath('//loc[contains(text(), "/fachmarkt/")]')
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        js_block = "".join(tree.xpath("//div/@data-google-map-options"))
        js = json.loads(js_block)
        a = js.get("storeData")
        location_name = (
            "".join(tree.xpath("//h1//text()")).replace("\n", "").strip() or "<MISSING>"
        )
        street_address = a.get("address1") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("countryCode")
        phone = a.get("phone") or "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        hours = a.get("storeHours")
        hours_of_operation = "<MISSING>"
        if hours:
            hours_of_operation = "".join(hours).replace("\n", " ").strip()
        store_number = a.get("storeId") or "<MISSING>"

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
