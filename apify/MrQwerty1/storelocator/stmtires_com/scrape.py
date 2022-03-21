from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = set()
    r = session.get("https://locations.stmtires.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc/text()")
    for link in links:
        if link.count("/") == 5:
            urls.add(f"{link}.json")

    return urls


def get_data(api, sgw: SgWriter):
    r = session.get(api, headers=headers)
    j = r.json()["profile"]
    page_url = api.replace(".json", "")
    location_name = j.get("name")
    a = j.get("address") or {}
    adr1 = a.get("line1") or ""
    adr2 = a.get("line2") or ""
    street_address = f"{adr1} {adr2}".strip()
    city = a.get("city")
    state = a.get("region")
    postal = a.get("postalCode")

    try:
        phone = j["mainPhone"]["display"]
    except:
        phone = SgRecord.MISSING
    g = j.get("yextDisplayCoordinate") or {}
    latitude = g.get("lat")
    longitude = g.get("long")

    _tmp = []
    try:
        hours = j["hours"]["normalHours"]
    except:
        hours = []

    for h in hours:
        day = h.get("day")
        isclosed = h.get("isClosed")
        if isclosed:
            _tmp.append(f"{day}: Closed")
            continue

        try:
            i = h.get("intervals")[0]
        except:
            i = dict()

        start = str(i.get("start")).zfill(4)
        end = str(i.get("end")).zfill(4)
        start = start[:2] + ":" + start[2:]
        end = end[:2] + ":" + end[2:]
        _tmp.append(f"{day}: {start}-{end}")

    hours_of_operation = ";".join(_tmp)

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

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.stmtires.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
