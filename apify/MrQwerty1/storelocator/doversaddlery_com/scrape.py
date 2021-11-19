from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://stores.doversaddlery.com/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='home-store-list']//a/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://stores.doversaddlery.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1/text()")[0].strip()
    street_address = ", ".join(
        tree.xpath("//span[contains(@class, 'dovr-store-address-')]/text()")
    ).strip()
    city = "".join(tree.xpath("//span[@class='dovr-store-city']/text()")).strip()
    state = "".join(tree.xpath("//span[@class='dovr-store-state']/text()")).strip()
    postal = "".join(tree.xpath("//span[@class='dovr-store-zip']/text()")).strip()
    phone = "".join(tree.xpath("//span[@class='dovr-store-phone']/text()")).strip()
    country_code = "US"

    try:
        text = tree.xpath("//iframe/@src")[0]
        latitude, longitude = text.split("center=")[1].split(",")
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours = tree.xpath("//div[@class='dovr-store-hours-data']/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours) or SgRecord.MISSING

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
    locator_domain = "https://doversaddlery.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
