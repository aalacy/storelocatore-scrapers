from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    r = session.get("https://richardsfoodporium.com/locations/")
    tree = html.fromstring(r.text)
    return tree.xpath("//a[@class='box-link']/@href")


def get_data(url, sgw: SgWriter):

    locator_domain = "https://richardsfoodporium.com"
    page_url = url
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    street_address = "".join(tree.xpath('//div[@class="store-details"]/p[1]/text()'))
    ad = "".join(tree.xpath('//div[@class="store-details"]/p[2]/text()'))
    city = ad.split(",")[0]
    state = ad.split(",")[1].split()[0]
    postal = ad.split(",")[1].split()[-1]
    country_code = "US"
    location_name = "".join(tree.xpath('//h1/span[@class="fl-heading-text"]/text()'))
    phone = "".join(tree.xpath('//div[@class="store-details"]/p[3]/text()'))
    hours_of_operation = (
        " ".join(tree.xpath("//h4/following-sibling::p/text()"))
        .replace("\n", "")
        .strip()
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
        latitude=SgRecord.MISSING,
        longitude=SgRecord.MISSING,
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
