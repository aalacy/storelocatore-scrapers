from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def generate_ids():
    r = session.get("https://www.quicklane.com/en-us/service-centers")
    tree = html.fromstring(r.text)
    out = []
    ids = tree.xpath("//h5/a[@class='store-url']/@href")
    for i in ids:
        out.append(i.split("/")[-2])
    return out


def get_data(store_number, sgw: SgWriter):
    r = session.get(
        f"https://www.digitalservices.ford.com/ql/api/v2/dealer?dealer={store_number}",
        headers=headers,
    )
    js = r.json()["qlDealer"]

    j = js.get("dealer") or {}
    try:
        s = js["seo"]["quickLaneInfo"]
    except:
        s = {}

    if not j and not s:
        return
    street_address = s.get("streetAddress") or j.get("streetAddress")
    city = s.get("city") or j.get("city")
    location_name = j.get("dealerName")
    state = s.get("state") or j.get("state")
    postal = s.get("zipCode") or j.get("zip")
    country_code = j.get("country")
    page_url = f"https://www.quicklane.com/en-us/oil-change-tire-auto-repair-store/{state}/{city}/{postal}/-/{store_number}"
    phone = s.get("phone") or ""
    if phone.strip() == ".":
        phone = SgRecord.MISSING
    latitude = j.get("latitude")
    longitude = j.get("longitude")

    _tmp = []
    for cnt in range(1, 5):
        key = f"hours{cnt}"
        val = s.get(key)
        if val:
            _tmp.append(val)

    hours_of_operation = ";".join(_tmp)

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
        store_number=store_number,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = generate_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.quicklane.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Origin": "https://www.quicklane.com",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
