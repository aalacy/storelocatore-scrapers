from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog


def get_urls():
    r = session.get("https://mayweather.fit/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='block col-12 col-md-6 col-xl-3']//a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).strip()
    line = tree.xpath(
        "//a[contains(@href, 'maps')]/text()|//div[@class='col-12 col-sm-4']/text()"
    )
    line = list(filter(None, [li.strip() for li in line]))
    logger.info(f"{page_url}: {line}")
    street_address = line.pop(0)
    csz = line.pop(0)
    city = csz.split(", ")[0]
    sz = csz.split(", ")[-1]
    state, postal = sz.split()
    country_code = "US"
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/text()")).strip()
    latitude = "".join(tree.xpath("//div[@class='marker']/@data-lat")).strip()
    longitude = "".join(tree.xpath("//div[@class='marker']/@data-lng")).strip()

    hours_of_operation = SgRecord.MISSING
    if tree.xpath("//span[contains(text(), 'COMING SOON')]"):
        hours_of_operation = "Coming Soon"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
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
    locator_domain = "https://mayweather.fit/"
    logger = sglog.SgLogSetup().get_logger(logger_name="mayweather.fit")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
