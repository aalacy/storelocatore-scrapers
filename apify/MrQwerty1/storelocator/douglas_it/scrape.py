import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.douglas.it/storelist", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class='rd__letters-listing__letter__stores__store']/a[@class='rd__link']/@href"
    )


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.douglas.it{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'DglStaticData =')]/text()")
    ).strip()
    text = text.split("DglStaticData =")[1].split("}};")[0] + "}}"
    j = json.loads(text)["storeDetails"]

    location_name = " ".join(" ".join(tree.xpath("//h1//text()")).split())
    a = j.get("address") or {}
    street = a.get("street") or ""
    number = a.get("number") or ""
    street_address = f"{street} {number}".strip()
    street_address = street_address.replace("(", "").replace(")", "").strip()
    city = a.get("city")
    postal = a.get("zip")
    country_code = "IT"
    phone = j.get("phone")
    store_number = j.get("code")

    c = j.get("coordinates")
    latitude = c.get("latitude")
    longitude = c.get("longitude")

    _tmp = []
    hours = j.get("openingHours") or []
    for h in hours:
        day = h.get("days")
        inter = h.get("time")
        _tmp.append(f"{day}: {inter}")

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
    locator_domain = "https://www.douglas.it/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
