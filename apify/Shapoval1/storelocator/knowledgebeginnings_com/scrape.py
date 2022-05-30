from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from concurrent import futures
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://www.kindercare.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//loc[contains(text(), '/our-centers/')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.knowledgebeginnings.com/"
    page_url = "".join(url)
    if page_url.count("/") != 6:
        return
    store_number = page_url.split("/")[-1].strip()
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath('//h1[@itemprop="name"]/text()')) or "<MISSING>"
    street_address = (
        "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()')) or "<MISSING>"
    )
    city = (
        "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()')) or "<MISSING>"
    )
    state = (
        "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()')) or "<MISSING>"
    )
    postal = "".join(tree.xpath('//span[@itemprop="postalCode"]/text()')) or "<MISSING>"
    country_code = "US"
    phone = "".join(tree.xpath('//span[@itemprop="telephone"]//text()')) or "<MISSING>"
    if "Fax" in phone:
        phone = phone.split("Fax")[0].strip()
    latitude = "".join(tree.xpath('//meta[@itemprop="latitude"]/@content'))
    longitude = "".join(tree.xpath('//meta[@itemprop="longitude"]/@content'))
    hours_of_operation = "".join(tree.xpath('//*[@itemprop="openingHours"]/@datetime'))

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


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=7) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
