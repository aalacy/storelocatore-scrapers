from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="office.co.uk")


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def get_urls():
    r = session.get(
        "https://www.office.co.uk/view/content/storelocator", headers=headers
    )
    log.info(f"Get URLs: {r}")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[contains(@id, 'addressDetail')]/a/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.office.co.uk/view/content/storelocator{slug}"
    r = session.get(page_url, headers=headers)
    log.info(f"{page_url} Response: {r}")
    tree = html.fromstring(r.text)

    line = tree.xpath(
        "//ul[@class='storelocator_addressdetails_address darkergrey']/li/text()"
    )
    line = list(filter(None, [li.strip() for li in line]))
    if line:
        location_name = line.pop(0)
    else:
        location_name = SgRecord.MISSING

    raw_address = ", ".join(line)
    phone = "".join(
        tree.xpath(
            "//div[@class='storelocator_contactdetails floatProperties']/div[1]/text()"
        )
    ).strip()

    street_address, city, postal = get_international(raw_address)
    country_code = "GB"
    if " " not in postal and postal != SgRecord.MISSING:
        country_code = "DE"

    text = "".join(tree.xpath("//script[contains(text(),'LatLng')]/text()"))
    try:
        latitude, longitude = eval(text.split("LatLng")[1].split(");")[0])
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    hours = tree.xpath("//ul[@class='storelocator_open_times_content']/li//text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    for h in hours:
        if h.endswith("-"):
            continue
        _tmp.append(h)

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    log.info(f"Total URLs to crawl: {len(urls)}")
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.office.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    }
    session = SgRequests(proxy_country="gb")
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
