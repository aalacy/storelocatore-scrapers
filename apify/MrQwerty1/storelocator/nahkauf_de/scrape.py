from concurrent import futures
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_additional(url):
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//div[@class='selected-shop__opening--day']")
    for h in hours:
        day = "".join(h.xpath(".//text()")).strip()
        inter = "".join(h.xpath("./following-sibling::div[1]//text()")).strip()
        _tmp.append(f"{day}: {inter}")
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/text()")).strip()

    return phone, ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    add = dict()
    api = "https://nahkauf.de/.rest/nk/markets/list"
    r = session.get(api, headers=headers)
    js = r.json()

    urls = []
    for j in js:
        slug = j.get("link")
        urls.append(f"https://nahkauf.de{slug}")

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_additional, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            key = future_to_url[future].split("/")[-1]
            add[key] = future.result()

    for j in js:
        location_name = j.get("name")
        street_address = j.get("street")
        city = j.get("city")
        postal = j.get("zipCode")
        country_code = "DE"
        store_number = j.get("id")
        slug = j.get("link")
        page_url = f"https://nahkauf.de{slug}"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        if str(latitude) == "0.0":
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        key = page_url.split("/")[-1]
        phone, hours_of_operation = add.get(key) or (SgRecord.MISSING, SgRecord.MISSING)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://nahkauf.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
