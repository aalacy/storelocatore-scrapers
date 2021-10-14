from lxml import html
from concurrent import futures
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get("https://toshop.ru/sitemap/sitemap_2.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://toshop.ru/"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    ad = "".join(
        tree.xpath(
            '//span[@id="lblBlockMain"]/b[contains(text(), "адрес магазина:")]/following-sibling::li[1]/text()'
        )
    )
    a = parse_address(International_Parser(), ad)
    street_address = (
        f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
        or "<MISSING>"
    )
    if street_address == "<MISSING>":
        street_address = (
            "".join(
                tree.xpath(
                    '//span[@id="lblBlockMain"]/b[contains(text(), "адрес магазина:")]/following-sibling::li[1]/text()'
                )
            )
            or "<MISSING>"
        )
    if street_address == "<MISSING>":
        return

    state = a.state or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    country_code = "RU"
    location_name = (
        "".join(tree.xpath('//h1[@class="inline_main"]/text()[1]')) or "<MISSING>"
    )
    try:
        city = location_name.split("-")[1].strip()
    except:
        city = a.city or "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                '//span[@id="lblBlockMain"]/b[contains(text(), "телефон")]/following-sibling::li[1]/text()'
            )
        )
        or "<MISSING>"
    )
    if phone.find(",") != -1:
        phone = phone.split(",")[0].strip()
    if phone.find(";") != -1:
        phone = phone.split(";")[0].strip()
    try:
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "YMaps.GeoPoint")]/text()'))
            .split("YMaps.GeoPoint(")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "YMaps.GeoPoint")]/text()'))
            .split("YMaps.GeoPoint(")[1]
            .split(",")[1]
            .split(")")[0]
            .strip()
        )
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"
    if latitude == "<MISSING>":
        try:
            latitude = (
                "".join(
                    tree.xpath('//a[contains(text(), "посмотреть на карте")]/@href')
                )
                .split("Geo=")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(
                    tree.xpath('//a[contains(text(), "посмотреть на карте")]/@href')
                )
                .split("Geo=")[1]
                .split(",")[1]
                .split("&")[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
    hours_of_operation = (
        "".join(
            tree.xpath(
                '//span[@id="lblBlockMain"]/b[contains(text(), "часы работы:")]/following-sibling::li[1]/text()'
            )
        )
        .replace("\r\n", "")
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    hours_of_operation = " ".join(hours_of_operation.split())
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
    with futures.ThreadPoolExecutor(max_workers=7) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
