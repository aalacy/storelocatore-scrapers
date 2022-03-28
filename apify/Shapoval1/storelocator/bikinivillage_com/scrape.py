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
    r = session.get("https://www.bikinivillage.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), '/our-stores/')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.bikinivillage.com/"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = (
        "".join(tree.xpath('//div[@class="store-title mb-1"]/text()')) or "<MISSING>"
    )
    if location_name == "<MISSING>":
        return
    street_address = (
        "".join(
            tree.xpath(
                '//div[./i[@class="icon-icn-Location-line-small pr-1"]]/following-sibling::div[1]/span/span[1]/text()'
            )
        )
        or "<MISSING>"
    )
    ad = (
        "".join(
            tree.xpath(
                '//div[./i[@class="icon-icn-Location-line-small pr-1"]]/following-sibling::div[1]/span/span[2]/text()'
            )
        )
        or "<MISSING>"
    )
    city = ad.split(",")[0].strip()
    state = " ".join(ad.split(",")[1].split()[:-1]).strip()
    postal = ad.split(",")[1].split()[-1].strip()
    country_code = "CA"
    jsll = "".join(tree.xpath("//div/@data-stores-found"))
    js = json.loads(jsll)
    latitude = js.get("CenterLatitude") or "<MISSING>"
    longitude = js.get("CenterLongitude") or "<MISSING>"
    phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
    if phone == "TBD":
        phone = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//div[@class="col-10 d-sm-block d-none pt-1"]/div/div/div/text()'
            )
        )
        .replace("\n", "")
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
        raw_address=f"{street_address} {ad}",
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
