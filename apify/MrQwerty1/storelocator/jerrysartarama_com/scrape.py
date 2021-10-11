from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.jerryswholesalestores.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(text(), 'Store Information')]/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.jerryswholesalestores.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    phone = "".join(tree.xpath("//footer//a[contains(@href, 'tel:')]/text()")).strip()
    street_address = "".join(
        tree.xpath(
            "//footer//div[@class='street-address']/text()|//footer//div[@class='extended-address']/text()"
        )
    ).strip()
    city = "".join(tree.xpath("//footer//span[@class='locality']/text()")).strip()
    state = "".join(tree.xpath("//footer//span[@class='region']/text()")).strip()
    postal = "".join(tree.xpath("//footer//span[@class='postal-code']/text()")).strip()
    location_name = f"{city}, {state}"
    country_code = "US"

    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    try:
        if "@" not in text:
            latitude, longitude = text.split("dir/")[1].split("/")[0].split(",")
        else:
            latitude, longitude = text.split("/@")[1].split(",")[:2]
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    _tmp = []
    lines = tree.xpath("//footer//p//text()")
    for line in lines:
        if not line.strip() or "Yes" in line:
            continue
        if ":" not in line:
            _tmp.append(f"{line.strip()};")
        else:
            _tmp.append(line.strip())

    hours_of_operation = "".join(_tmp)[:-1]

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
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
    locator_domain = "https://jerrysartarama.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
