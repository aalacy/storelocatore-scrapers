import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def get_urls():
    urls = []
    ccs = ["uk", "fr", "es", "at"]
    for cc in ccs:
        r = session.get(f"https://{cc}.westfield.com/", headers=headers)
        tree = html.fromstring(r.text)
        slugs = tree.xpath("//a[@class='js-centre-name']/@href")
        for slug in slugs:
            urls.append(f"https://{cc}.westfield.com{slug}/access")

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[contains(@class, 'center-name')]/text()")
    ).strip()
    line = tree.xpath("//div[@class='center-address']/text()")
    line = list(filter(None, [li.strip() for li in line]))
    raw_address = ", ".join(line)
    if raw_address.count(" - ") == 2:
        raw_address = raw_address.split(" - ")[-1]
    street_address, city, postal = get_international(raw_address)
    if postal == SgRecord.MISSING:
        postal = "".join(re.findall(r"\d{4,5}", raw_address))
    country_code = page_url.split(".")[0].split("/")[-1].upper()
    locator_domain = f"https://{country_code.lower()}.westfield.com/"
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/text()")).strip()
    latitude = "".join(tree.xpath("//div/@data-latitude"))
    longitude = "".join(tree.xpath("//div/@data-longitude"))

    _tmp = []
    hours = tree.xpath("//li[contains(@class, 'item-date d-flex flex-lg-row')]")
    for h in hours:
        day = "".join(h.xpath("./span[1]/text()")).strip()
        inter = "".join(h.xpath("./span[2]/text()")).strip()
        _tmp.append(f"{day}: {inter}")
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
        raw_address=raw_address,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
