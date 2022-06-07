import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.cropp.com/special/store/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='cart']/@href")


def get_data(slug, sgw: SgWriter):
    api = f"https://www.cropp.com{slug}ajx/stores/get/"
    page_url = f"https://www.cropp.com{slug}storelocator"
    r = session.post(api, headers=headers)
    js = r.json()["content"]["stores"]

    for j in js:
        location_name = j.get("name")
        street_address = j.get("street")
        zc = j.get("city") or ""
        postal = "".join(re.findall(r"\d+.\d+", zc))
        city = zc.replace(postal, "").strip()
        if city[-1].isdigit():
            city = " ".join(city.split()[:-1])

        country_code = slug.split("/")[1].upper()
        phone = j.get("phone") or ""
        if "/" in phone:
            phone = phone.split("/")[0].strip()
        if "доб" in phone:
            phone = phone.split("доб")[0].strip()
        phone = " ".join(phone.split()[1:])
        if '"' in phone:
            phone = phone.split('"')[-1].strip()
        if "ka" in phone:
            phone = phone.split("ka")[-1].strip()
        store_number = j.get("id")

        g = j.get("location")
        latitude = g.get("lat")
        longitude = g.get("lng")

        location_type = j.get("departments")
        hours = j.get("open_hours") or []
        hours_of_operation = ";".join(hours)

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
            location_type=location_type,
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
    locator_domain = "https://www.cropp.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
