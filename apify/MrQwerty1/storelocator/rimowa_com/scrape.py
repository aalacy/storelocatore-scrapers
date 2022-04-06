import json
import country_converter as coco
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    api_url = "https://www.rimowa.com/on/demandware.store/Sites-Rimowa-Site/en_US/GeoJSON-AllStores?filterServices=STORE"

    r = session.get(api_url, headers=headers)
    js = r.json()["features"]

    for j in js:
        j = j.get("properties")
        urls.append(f"https://www.rimowa.com/us/en/storedetails/-/-{j.get('ID')}")

    return urls


def get_data(page_url, sgw: SgWriter):
    cc = coco.CountryConverter()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'addressLocality')]/text()"))
    j = json.loads(text)

    location_name = j.get("name")
    page_url = r.url
    a = j.get("address") or {}
    street_address = a.get("streetAddress") or ""
    city = a.get("addressLocality") or ""
    postal = a.get("postalCode") or ""
    country = a.get("addressCountry")
    country_code = cc.convert(names=[country], to="ISO2")
    phone = j.get("telePhone") or ""
    g = j.get("geo") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")
    location_type = j.get("@type")
    hours_of_operation = j.get("openingHours") or ""

    if (postal == "" or postal == "null") and street_address.split()[-1][0].isdigit():
        postal = street_address.split()[-1]

    if "Century" in postal:
        postal = SgRecord.MISSING

    if hours_of_operation == "" or hours_of_operation == "null":
        _tmp = []
        tr = tree.xpath("//div[@class='hours-list-item']")
        for t in tr:
            day = "".join(t.xpath("./div[1]/text()")).strip()
            inter = "".join(t.xpath("./div[2]/text()")).strip()
            _tmp.append(f"{day}: {inter}")
        hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address.replace("null", "").strip(),
        city=city.replace("null", "").strip(),
        zip_postal=postal.replace("null", "").strip(),
        country_code=country_code,
        phone=phone.replace("null", "").strip(),
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation.replace("null", "").strip(),
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.rimowa.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Cache-Control": "max-age=0, no-cache",
        "Referer": "https://www.rimowa.com/gb/en/storelocator",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
