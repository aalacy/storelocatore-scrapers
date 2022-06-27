from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgzip.dynamic import SearchableCountries, DynamicZipSearch


def get_urls():
    urls = set()
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.johnsonfitness.com",
        "Connection": "keep-alive",
        "Referer": "https://www.johnsonfitness.com/StoreLocator/Index?lat=&lon=",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
    }

    params = (
        ("lat", ""),
        ("lon", ""),
    )
    for _zip in search:
        data = {
            "submitted": "1",
            "view_type": "Home",
            "cbFilter": "",
            "searchZip": str(_zip),
        }

        r = session.post(
            "https://www.johnsonfitness.com/StoreLocator/Index",
            headers=headers,
            params=params,
            data=data,
        )
        tree = html.fromstring(r.text)
        links = tree.xpath("//div[contains(@class, 'single')]//h3/a/@href")
        for link in links:
            urls.add(link)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//span[@itemprop='name']/text()")).strip()
    if not location_name:
        return

    street_address = " ".join(
        "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).split()
    )
    if street_address.find("(") != -1:
        street_address = street_address.split("(")[0].strip()
    if street_address.find("USA") != -1:
        street_address = street_address.split(",")[0].strip()

    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = (
        "".join(tree.xpath("//p[@itemprop='address']/text()")).replace(",", "").strip()
    )
    try:
        phone = tree.xpath("//span[@itemprop='telephone']/text()")[0].strip()
    except IndexError:
        phone = SgRecord.MISSING
    latitude = "".join(tree.xpath("//meta[@itemprop='latitude']/@content"))
    longitude = "".join(tree.xpath("//meta[@itemprop='longitude']/@content"))
    hours_of_operation = ";".join(
        tree.xpath("//meta[@itemprop='openingHours']/@content")
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
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
    locator_domain = "https://2ndwindexercise.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
