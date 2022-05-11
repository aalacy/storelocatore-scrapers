from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://douglas.es/g/nuestras_tiendas", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='rd__nav-item sd__nav-item rd__nav-item--90 rd__link']/@href"
    )


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//meta[@itemprop='name']/@content"))
    street_address = "".join(
        tree.xpath("//span[@itemprop='streetAddress']/text()")
    ).strip()
    if street_address.endswith(","):
        street_address = street_address[:-1].strip()
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    country_code = "ES"
    phone = "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()
    store_number = page_url.split("/")[-1]

    text = "".join(tree.xpath("//script[contains(text(), 'var llat=')]/text()"))
    try:
        latitude = text.split("var llat=")[1].split(",")[0]
        longitude = text.split("llon=")[1].split(";")[0]
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours_of_operation = ";".join(
        tree.xpath("//span[contains(text(), 'Horario')]/following-sibling::span/text()")
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
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

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://douglas.es/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
