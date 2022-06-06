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
    }
    r = session.get("https://www.metro.de/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)

    return tree.xpath("//url/loc[contains(text(), '/standorte/')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.metro.de/"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    ad = (
        "".join(tree.xpath('//a[@class="store-address"]/text()'))
        .replace(
            "Dresdener Straße, 57, 02625 Bautzen", "Dresdener Straße 57, 02625 Bautzen"
        )
        .replace(
            "Lärchenstraße, 4, 76532 Baden-Baden", "Lärchenstraße 4, 76532 Baden-Baden"
        )
        .replace("\n", "")
        .strip()
    )
    if not ad:
        return
    street_address = ad.split(",")[0].strip()
    if street_address.find("(") != -1:
        street_address = street_address.split("(")[0].strip()
    adr = ad.split(",")[1].replace("17491Greifswald", "17491 Greifswald").strip()
    if adr.find("(") != -1:
        adr = adr.split("(")[0].strip()
    state = "<MISSING>"
    postal = adr.split()[0].strip()
    country_code = "DE"
    city = " ".join(adr.split()[1:])
    if city.find("/") != -1:
        city = city.split("/")[0].strip()

    location_name = "".join(tree.xpath('//h1[@class="store-name"]/text()'))
    phone = (
        "".join(tree.xpath('//a[@class="store-phone"]/text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    ll = "".join(tree.xpath('//a[@class="store-address"]/@href'))
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    if ll:
        latitude = ll.split("=")[-1].split(",")[0].strip()
        longitude = ll.split("=")[-1].split(",")[1].strip()
    _tmp = []
    days = tree.xpath(
        '//div[text()="Allgemein"]/following-sibling::div[1]/div[1]/span/text()'
    )
    times = tree.xpath(
        '//div[text()="Allgemein"]/following-sibling::div[1]/div[2]/span/text()'
    )
    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")
    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.endswith(";Sonntag: -"):
        hours_of_operation = hours_of_operation.replace(";Sonntag: -", "").strip()

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
        raw_address=ad,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
