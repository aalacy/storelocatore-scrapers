import json
from concurrent import futures
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_urls():
    urls = []
    r = session.get("https://www.carinos.com/locations/")
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'carinos.locations.list')]/text()")
    )
    text = (
        text.split("carinos.locations.list = ")[1]
        .split("carinos.locations")[0]
        .strip()[:-1]
    )
    js = json.loads(text)

    for j in js:
        urls.append(f'https://www.carinos.com{j.get("url")}')

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//location-current")[0].get(":loc-query"))
    j = json.loads(text)

    location_name = j.get("name")
    street_address = f'{j.get("address")} {j.get("address2") or ""}'.strip()
    city = j.get("city")
    state = j.get("state")
    postal = j.get("zip")
    store_number = j.get("storeIdentifier")
    phone = j.get("phone")
    latitude = j.get("lat")
    longitude = j.get("lng")

    _tmp = []
    divs = tree.xpath("//div[@class='group-hour-day']")

    for d in divs:
        day = "".join(d.xpath("./div[@class='name-day']/text()")).strip()
        time = "".join(d.xpath(".//li//text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        store_number=store_number,
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
    locator_domain = "https://www.carinos.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
