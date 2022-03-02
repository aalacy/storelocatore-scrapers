from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_cookies():
    r = session.get("https://www.kikocosmetics.com/en-gb/")

    return {"JSESSIONID": r.cookies["JSESSIONID"]}


def get_urls():
    urls = []
    r = session.get(
        "https://www.kikocosmetics.com/eshop/storelocator/all", cookies=cookies
    )
    js = r.json()["features"]

    for j in js:
        slug = j["properties"]["url"]
        urls.append(f"https://www.kikocosmetics.com{slug}")

    return urls


def get_data(page_url, sgw: SgWriter):
    try:
        r = session.get(page_url)
        tree = html.fromstring(r.text)
    except:
        return

    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")[-1]).strip()
    try:
        street_address = tree.xpath("//span[@itemprop='streetAddress']/text()")[
            -1
        ].strip()
    except IndexError:
        street_address = SgRecord.MISSING
    try:
        city = tree.xpath("//span[@itemprop='addressLocality']/text()")[-1].strip()
    except IndexError:
        city = SgRecord.MISSING
    state = SgRecord.MISSING
    try:
        postal = tree.xpath("//span[@itemprop='postalCode']/text()")[-1].strip()
    except IndexError:
        postal = SgRecord.MISSING
    try:
        country_code = tree.xpath("//span[@itemprop='addressCountry']/text()")[
            -1
        ].strip()
    except IndexError:
        country_code = SgRecord.MISSING
    try:
        phone = tree.xpath("//span[@itemprop='telephone']/text()")[-1].strip()
    except IndexError:
        phone = SgRecord.MISSING
    try:
        latitude = tree.xpath("//meta[@itemprop='latitude']/@content")[-1]
    except IndexError:
        latitude = SgRecord.MISSING
    try:
        longitude = tree.xpath("//meta[@itemprop='longitude']/@content")[-1]
    except IndexError:
        longitude = SgRecord.MISSING

    hours_of_operation = ";".join(tree.xpath("//dl[@itemprop='openingHours']/@content"))

    row = SgRecord(
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
    locator_domain = "https://www.kikocosmetics.com/"
    session = SgRequests()
    cookies = get_cookies()

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
