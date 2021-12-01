from sgpostal.sgpostal import International_Parser, parse_address
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
    r = session.get("https://www.curves.eu/curves-sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.anthonys.com"
    page_url = "".join(url)
    if page_url.count("/") != 6:
        return

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    ad = tree.xpath(
        '//div[./div/div/img[@class="attachment-large size-large"]]/preceding-sibling::div//text()'
    )
    location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
    ad = list(filter(None, [a.strip() for a in ad]))
    phone = "".join(ad[-1]).strip()
    adr = " ".join(ad[1:-1])

    a = parse_address(International_Parser(), adr)
    street_address = " ".join(ad[:-3]).replace(f"{location_name}", "").strip()
    state = a.state or "<MISSING>"
    postal = "".join(ad[-3])
    country_code = (
        page_url.split("https://www.curves.eu/")[1].split("/")[0].upper().strip()
    )
    if country_code == "EN":
        country_code = "UK"
    city = a.city or "<MISSING>"

    latitude = "".join(tree.xpath("//div/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div/@data-lng")) or "<MISSING>"
    hours_of_operation = (
        " ".join(tree.xpath("//table//tr/td/text()")).replace("\n", "").strip()
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
        raw_address=adr,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
