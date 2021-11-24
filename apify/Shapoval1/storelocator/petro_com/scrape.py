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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://www.petro.com/petro-locations", headers=headers)

    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='addressListing']/a/@href")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.petro.com"
    page_url = f"https://www.petro.com{url}"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    ad = tree.xpath('//div[@class="street"]/p/text()')
    ad = list(filter(None, [a.strip() for a in ad]))
    street_address = " ".join(ad[:-1])
    ad = ad[-1]
    if ad.count(",") == 2:
        ad = ad.replace(",", "")
    if ad.find(",") != -1:
        city = ad.split(",")[0].strip()
        ad = ad.split(",")[1].strip()
    else:
        city = " ".join(ad.split()[:-2])
        ad = ad.replace(city, "").strip()
    state = ad.split()[0]
    postal = ad.split()[1]
    country_code = "US"

    location_name = f"Petro Home Services {city}, {state}"
    phone = (
        "".join(tree.xpath('//p[contains(text(), "Sales")]/a[1]/text()'))
        .replace("Sales:", "")
        .strip()
        or "<MISSING>"
    )
    if phone.find("\n") != -1:
        phone = phone.split("\n")[0]
    map_link = "".join(tree.xpath("//iframe/@src"))
    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
        hours_of_operation=SgRecord.MISSING,
    )

    sgw.write_row(row)


def fetch_data(sgw):

    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
