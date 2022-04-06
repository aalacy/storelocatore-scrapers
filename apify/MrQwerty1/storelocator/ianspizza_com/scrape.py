from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://ianspizza.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='link-expander tippy-title']/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/span[not(@style)]/text()")).strip()
    a = tree.xpath("//h1/following-sibling::a")[0]
    street = "".join(a.xpath(".//span[@class='segment-street_number']/text()")).strip()
    street_name = "".join(
        a.xpath(".//span[@class='segment-street_name']/text()")
    ).strip()
    street_address = f"{street} {street_name}"
    city = "".join(a.xpath(".//span[@class='segment-city']/text()")).strip()
    state = "".join(a.xpath("./p/text()")).replace(",", "").strip()
    postal = "".join(a.xpath(".//span[@class='segment-post_code']/text()")).strip()
    country_code = "US"
    try:
        phone = tree.xpath("//a[contains(@href, 'tel:')]/text()")[0].strip()
        if "," in phone:
            phone = phone.split(",")[0].strip()
    except IndexError:
        phone = SgRecord.MISSING

    latitude = tree.xpath("//div[@class='marker']/@data-lat")[0]
    longitude = tree.xpath("//div[@class='marker']/@data-lng")[0]
    hours_of_operation = (
        "".join(tree.xpath("//p[contains(text(), 'Hours:')]/text()"))
        .replace("Hours:", "")
        .strip()
    )

    row = SgRecord(
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
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://ianspizza.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
