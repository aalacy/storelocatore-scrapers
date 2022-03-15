import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures
from sgpostal.sgpostal import International_Parser, parse_address


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://brownssocialhouse.com/",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://brownssocialhouse.com/#locations-section", headers=headers)
    tree = html.fromstring(r.content)

    return tree.xpath("//a[./strong][not(contains(@href, '#'))]/@href")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://brownssocialhouse.com/"
    page_url = "".join(url)
    if page_url.count("/") == 4:
        page_url = (
            " ".join(page_url.split("/")[:-1]).split()[-1].replace("/", "").strip()
        )
    if page_url.count("/") == 3:
        page_url = page_url.split("/")[-1].replace("/", "").strip()
    if page_url.count("/") == 1:
        page_url = page_url.split("/")[-1].replace("/", "").strip()
    page_url = f"https://brownssocialhouse.com/{page_url}"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://brownssocialhouse.com/",
        "Proxy-Authorization": "Basic VEYwYmJlZGNkNWM1YmE1YWZjNDhhOTQ4MjcxMDlmMGJhMS5oNzgzb2hhdzA5amRmMDpURjBiYmVkY2Q1YzViYTVhZmM0OGE5NDgyNzEwOWYwYmExLmg3ODIzOWhk",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h3/strong[contains(text(), "HOURS")]/following::p/text() | //h3/strong[contains(text(), "hOURS")]/following::p/text() | //h3[./strong[text()="HOURS OF OPERATION"]]/following-sibling::p[1]/text() | //h3[./strong[text()="Hours of operation"]]/following-sibling::p[1]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    ) or "<MISSING>"
    hours_of_operation = " ".join(hours_of_operation.split())
    if hours_of_operation.find("Serving") != -1:
        hours_of_operation = hours_of_operation.split("Serving")[0].strip()
    if hours_of_operation.find("We ") != -1:
        hours_of_operation = hours_of_operation.split("We ")[0].strip()
    if hours_of_operation.find("!") != -1:
        hours_of_operation = hours_of_operation.split("!")[1].strip()
    js = "".join(
        tree.xpath('//div[@class="sqs-block map-block sqs-block-map"]/@data-block-json')
    )
    j = json.loads(js)
    street_address = "".join(j.get("location").get("addressLine1")).strip()
    ad = "".join(j.get("location").get("addressLine2"))
    a = parse_address(International_Parser(), ad)
    postal = a.postcode or "<MISSING>"
    if street_address.find("9719") != -1:
        postal = "V1J 3X9"
    if street_address.find("8120") != -1:
        street_address = "8120 44TH Street"
        postal = "T0B 0L0"
    city = a.city
    state = a.state
    country_code = "".join(j.get("location").get("addressCountry"))
    location_name = "".join(j.get("location").get("addressTitle"))
    if page_url.find("portage") != -1:
        postal = tree.xpath('//div[@class="page-description"]/p[1]/text()')
        postal = "".join(postal[0]).split(",")[-1].strip()
    phone = (
        "".join(
            tree.xpath(
                '//div[@class="page-description"]/p[2][contains(text(), "(")]//text() | //div[@class="page-description"]/p[3][contains(text(), "(")]//text() | //div[@class="page-description"]/p/a[contains(text(), "(")]//text() | //div[@class="page-description"]/p[2][contains(text(), "-")]//text()'
            )
        )
        or "<MISSING>"
    )
    if phone.find("BC") != -1:
        phone = phone.split("BC")[1].strip()
    if phone.find("ORDER") != -1:
        phone = phone.split("ORDER")[0].strip()
    latitude = j.get("location").get("mapLat")
    longitude = j.get("location").get("mapLng")
    if (
        page_url.find("harvey") != -1
        or page_url.find("qetheatre") != -1
        or page_url.find("st-albert") != -1
        or page_url.find("portage") != -1
    ):
        phone = tree.xpath('//div[@class="page-description"]/p[1]//text()')
        phone = "".join(phone[-1])

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
