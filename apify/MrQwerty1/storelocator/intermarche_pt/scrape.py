import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog


def get_urls():
    urls = set()
    api = "https://www.intermarche.pt/umbraco/Api/Pos/Get"
    r = session.get(api, headers=headers)
    logger.info(f"{api}: {r.status_code}")
    js = json.loads(json.loads(r.text))["list"]

    for j in js:
        urls.add(j.get("url"))

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    logger.info(f"{page_url}: {r.status_code}")
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip()
    street_address = "".join(
        tree.xpath("//span[@itemprop='streetAddress']/text()")
    ).strip()
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    if " " in postal:
        postal = postal.split()[0].strip()
    country_code = "PT"
    try:
        phone = tree.xpath("//a[@itemprop='telephone']/text()")[0].strip()
    except IndexError:
        phone = SgRecord.MISSING
    store_number = "".join(tree.xpath("//div[@id='pos-map']/@data-pos"))
    latitude = "".join(tree.xpath("//div[@id='pos-map']/@data-latitude"))
    longitude = "".join(tree.xpath("//div[@id='pos-map']/@data-longitude"))
    hours_of_operation = ";".join(tree.xpath("//span[@itemprop='time']/text()")).strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    logger.info(f"{len(urls)} URLs are ready to crawl")

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.intermarche.pt/"
    logger = sglog.SgLogSetup().get_logger(logger_name="intermarche.pt")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
