from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.honda.se/cars/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath(
        "//url/loc[contains(text(), 'https://www.honda.se/cars/dealers/')]/text()"
    )


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.honda.se/"
    page_url = url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    street_address = (
        "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
        .replace("\n", "")
        .strip()
    )
    if street_address.find("(") != -1:
        street_address = street_address.split("(")[0].replace(",", "").strip()
    city = "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
    postal = "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
    country_code = "SE"
    location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                '//section[@class="fad-dealer-details"]/following-sibling::section[1]//a[contains(@href, "tel")]/text()'
            )
        )
        or "<MISSING>"
    )
    if phone == "<MISSING>":
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
    hours_of_operation = "<MISSING>"
    text = "".join(tree.xpath("//a[./img]/@href"))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=SgRecord.MISSING,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
        raw_address=f"{street_address} {city} {postal}",
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
