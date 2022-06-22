import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.mrsfields.com/stores/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='state-list']//a/@href")


def get_hoo(page_url):
    _tmp = []
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    hours = tree.xpath(
        "//div[contains(text(), 'Hours')]/following-sibling::div/div/div"
    )
    for h in hours:
        inter = " ".join("".join(h.xpath(".//text()")).split())
        _tmp.append(inter)

    return ";".join(_tmp)


def get_data(url, sgw: SgWriter):
    api = f"{locator_domain}{url}"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var data =')]/text()"))
    text = text.split("var data = { data:")[1].split(" }")[0]
    js = json.loads(text)

    for j in js:
        location_name = j.get("name").strip()

        adr1 = j.get("address1") or ""
        adr2 = j.get("address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        if "events" in adr1.lower() and adr2:
            street_address = adr2
        elif "events" in adr1.lower() and not adr2:
            street_address = adr1.split("EVENTS")[-1]
        if "events" in adr2.lower():
            street_address = adr1
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"
        store_number = j.get("store_num")
        slug = j.get("store_url") or ""
        page_url = SgRecord.MISSING
        if slug:
            page_url = f"https://www.mrsfields.com{slug}"

        phone = j.get("phone") or ""
        if phone.count("0") == 10:
            phone = SgRecord.MISSING
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = str(j.get("store_hours") or "").replace("\n", ";")

        status = j.get("store_status") or ""
        if "temp" in status:
            hours_of_operation = "Temporarily Closed"
        elif "coming" in status:
            hours_of_operation = "Coming Soon"

        if not hours_of_operation and page_url != SgRecord.MISSING:
            hours_of_operation = get_hoo(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
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
    locator_domain = "https://www.mrsfields.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
