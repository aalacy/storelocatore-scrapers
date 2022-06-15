import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.douglas.it/it/l", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='link link--no-decoration list-view-item__link']/@href"
    )


def get_name(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    return " ".join(" ".join(tree.xpath("//h1//text()")).split())


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.douglas.it{slug}"
    store_number = page_url.split("/")[-1]
    api = f"https://www.douglas.it/api/v2/stores/{store_number}?fields=FULL"
    r = session.get(api, headers=headers)
    j = r.json()

    a = j.get("address") or {}
    raw_address = a.get("formattedAddress")
    location_name = j.get("displayName")
    if not location_name:
        location_name = get_name(page_url)
    adr1 = a.get("line1") or ""
    adr2 = a.get("line2") or ""
    street_address = f"{adr1} {adr2}"
    if "(" in street_address:
        street_address = street_address.split("(")[0].strip()

    postal = a.get("postalCode")
    city = a.get("town") or ""
    if "(" in city:
        city = city.split("(")[0].strip()
    city = city.replace(".", "").strip()
    country_code = "IT"
    phone = a.get("phone")

    g = j.get("geoPoint") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    _tmp = []
    try:
        hours = j["openingHours"]["weekDayOpeningList"]
    except:
        hours = []

    for h in hours:
        day = h.get("weekDayFull")
        if h.get("closed"):
            _tmp.append(f"{day}: Closed")
            continue

        start = h["openingTime"]["formattedHour"]
        end = h["closingTime"]["formattedHour"]
        _tmp.append(f"{day}: {start}-{end}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.douglas.it/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
