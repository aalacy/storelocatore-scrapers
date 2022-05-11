import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://magasins.picard.fr/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//loc/text()")[1:]


def get_data(url, sgw: SgWriter):
    locator_domain = "https://picard.fr/"
    sub_page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(sub_page_url, headers=headers)

    tree = html.fromstring(r.content)
    div = tree.xpath("//loc")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        try:
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            js_block = "".join(
                tree.xpath('//script[contains(text(), "streetAddress")]/text()')
            )
            js_block = " ".join(js_block.split())
            js = json.loads(js_block)
        except:
            continue
        a = js.get("address")
        street_address = a.get("streetAddress") or "<MISSING>"
        street_address = str(street_address).replace("&#039;", "`").strip()
        city = a.get("addressLocality") or "<MISSING>"
        state = "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("addressCountry") or "<MISSING>"
        location_name = js.get("name") or "<MISSING>"
        phone = js.get("telephone") or "<MISSING>"
        try:
            hours_of_operation = (
                "".join(js.get("openingHours"))
                .replace("\n", " ")
                .replace("\r", " ")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        except:
            hours_of_operation = "<MISSING>"
        latitude = js.get("geo").get("latitude")
        longitude = js.get("geo").get("longitude")

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


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
