from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(
        "https://hotheadburritos.com/locationfeed/getlocations.php", headers=headers
    )
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class='location-info']/a[1][contains(@href, '.com')]/@href"
    )


def get_id(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    return "".join(tree.xpath("//div[@id='storelanding']/div/@id"))


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_data(page_url, sgw: SgWriter):
    store_number = get_id(page_url)
    data = {"id": store_number}
    r = session.post(
        "https://hotheadburritos.com/locationfeed/locations-landing/landing.php",
        headers=headers,
        data=data,
    )
    tree = html.fromstring(r.text)

    if tree.xpath("//h1[contains(text(), 'Soon')]"):
        return

    location_name = "".join(tree.xpath("//div[@id='store-info']//h1/text()")).strip()
    line = tree.xpath(
        "//div[@class='col-sm-5']/a/text()|//div[@class='col-sm-5']/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    if street_address.endswith(","):
        street_address = street_address[:-1]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"

    phone = "".join(tree.xpath("//a[contains(@href, 'tel')]/text()")).strip()
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

    _tmp = []
    for i in range(7):
        _tmp.append(
            "".join(tree.xpath(f"//p[contains(@class, 'd{i}')]/text()")).strip()
        )
    hours_of_operation = ";".join(_tmp) or SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
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
    locator_domain = "https://hotheadburritos.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
