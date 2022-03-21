from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_types():
    r = session.get("https://locations.bloomingdales.com/")
    tree = html.fromstring(r.text)

    out = dict()
    _types = [
        ("AllStores", "Retail"),
        ("OutletStores", "Outlet"),
        ("Restaurants", "Restaurant"),
    ]
    for t in _types:
        _id = t[0]
        _type = t[1]
        li = tree.xpath(f"//div[@id='{_id}']//li[@class='c-LocationGridList-item']")
        for l in li:
            slug = "".join(l.xpath(".//h2/a/@href"))
            if not out.get(slug):
                out[slug] = _type
            else:
                out[slug] = f"{out[slug]}, {_type}"

    return out


def get_data(item, sgw: SgWriter):
    slug, location_type = item
    url = f"https://locations.bloomingdales.com/{slug}.json"
    page_url = url.replace(".json", "")
    r = session.get(url)
    j = r.json()

    street_address = (
        f"{j.get('address1')} {j.get('address2') or ''}".strip() or SgRecord.MISSING
    )
    city = j.get("city") or SgRecord.MISSING
    state = j.get("state") or SgRecord.MISSING
    postal = j.get("postalCode") or SgRecord.MISSING
    country_code = j.get("country") or SgRecord.MISSING
    location_name = f"{j.get('name')} {city}".strip()
    store_number = j.get("corporateCode") or SgRecord.MISSING
    phone = j.get("phone") or SgRecord.MISSING
    latitude = j.get("latitude") or SgRecord.MISSING
    longitude = j.get("longitude") or SgRecord.MISSING
    days = j.get("hours", {}).get("days") or []

    _tmp = []
    for d in days:
        day = d.get("day")[:3].capitalize()
        try:
            interval = d.get("intervals")[0]
            start = str(interval.get("start"))
            end = str(interval.get("end"))

            if len(start) == 3:
                start = f"0{start}"

            if len(end) == 3:
                end = f"0{end}"

            line = f"{day}  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
        except IndexError:
            line = f"{day}  Closed"

        _tmp.append(line)

    hours_of_operation = ";".join(_tmp) or SgRecord.MISSING
    if (
        hours_of_operation.count("Closed") == 7
        or location_name.lower().find("closed") != -1
    ):
        hours_of_operation = "Closed"

    if location_name.lower().find(":") != -1:
        location_name = location_name.split(":")[0].strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_types()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, item, sgw): item for item in urls.items()
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://bloomingdales.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
