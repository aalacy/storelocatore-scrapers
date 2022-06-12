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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://bodyalivefitness.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://bodyalivefitness.com/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath(
        "//li/a[contains(text(), 'Locations')]/following-sibling::ul/li/a/@href | //li/a[contains(text(), 'Locations')]/following-sibling::ul/li/ul/li/a/@href"
    )


def get_data(url, sgw: SgWriter):
    locator_domain = "https://bodyalivefitness.com/"
    page_url = "".join(url)
    if page_url.find("cincinnati") != -1:
        return
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://bodyalivefitness.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    street_address = (
        "".join(tree.xpath('//div[./h4[contains(text(), "(")]]/h4[1]/text()'))
        .replace("\n", "")
        .strip()
    )
    if street_address.find("350") != -1:
        street_address = street_address.split(")")[1]
    ad = (
        "".join(tree.xpath('//div[./h4[contains(text(), "(")]]/h4[2]/text()'))
        .replace("\n", "")
        .strip()
    )
    if page_url.find("https://bodyalivefitness.com/denver/") != -1:
        ad = "".join(
            tree.xpath('//div[@class="locations_hero-left"]/following::h4[2]/text()')
        )
    try:
        city = ad.split(",")[0]
        state = ad.split(",")[1].split()[0]
        postal = ad.split(",")[1].split()[-1]
    except:
        city, state, postal = "<MISSING>", "<MISSING>", "<MISSING>"
    country_code = "US"
    location_name = "".join(tree.xpath("//h2[@style='text-align: center']//text()"))
    phone = (
        "".join(tree.xpath('//div[./h4[contains(text(), "(")]]/h4[3]/text()'))
        .replace("\n", "")
        .strip()
    ) or "<MISSING>"
    if page_url.find("https://bodyalivefitness.com/denver/") != -1:
        location_name = "".join(
            tree.xpath('//div[@class="locations_hero-left"]/h2//text()')
        )
        street_address = "".join(
            tree.xpath('//div[@class="locations_hero-left"]/following::h4[1]/text()')
        )

    ll = "".join(tree.xpath('//div[@class="et_pb_code_inner"]/iframe/@src'))
    latitude = ll.split("!3d")[1].strip().split("!")[0].strip()
    longitude = ll.split("!2d")[1].strip().split("!")[0].strip()
    hours_of_operation = "<MISSING>"
    jsblock = "".join(
        tree.xpath('//script[contains(text(), "http://schema.org")]/text()')
    )
    js = json.loads(jsblock)
    for j in js["location"]:
        url = j.get("url")
        if page_url == url:
            hours_of_operation = " ".join(j.get("openingHours"))

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
