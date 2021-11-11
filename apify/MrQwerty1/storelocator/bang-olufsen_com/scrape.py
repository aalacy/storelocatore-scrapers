from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = set()
    q = session.get("https://stores.bang-olufsen.com/sitemap.xml")
    root = html.fromstring(q.content)
    sitemaps = root.xpath("//loc/text()")
    for sitemap in sitemaps:
        r = session.get(sitemap)
        tree = html.fromstring(r.content)
        links = tree.xpath("//*[@hreflang='en-US']/@href")
        for link in links:
            if link.count("/") == 7:
                urls.add(f"{link}.json")

    return urls


def get_data(url, sgw: SgWriter):
    r = session.get(url)
    try:
        j = r.json()["profile"]
    except:
        return

    page_url = url.replace(".json", "")
    location_name = f"{j.get('name')} {j.get('c_localGeomodifier') or ''}".strip()
    a = j.get("address") or {}
    street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
    city = a.get("city")
    state = a.get("region")
    postal = a.get("postalCode")
    country_code = a.get("countryCode")
    phone = (
        j.get("mainPhone").get("display") if j.get("mainPhone") else SgRecord.MISSING
    )
    loc = j.get("yextDisplayCoordinate", {}) or {}
    latitude = loc.get("lat")
    longitude = loc.get("long")
    days = j.get("hours", {}).get("normalHours") or []

    _tmp = []
    for d in days:
        day = d.get("day")[:3].capitalize()
        try:
            interval = d.get("intervals")[0]
            start = str(interval.get("start"))
            if start == "0":
                _tmp.append("24 hours")
                break
            end = str(interval.get("end"))

            if len(start) == 3:
                start = f"0{start}"

            if len(end) == 3:
                end = f"0{end}"

            line = f"{day}  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
        except IndexError:
            line = f"{day}  Closed"

        _tmp.append(line)

    holidays = j.get("hours", {}).get("holidayHours") or []
    cnt = 0
    for h in holidays:
        if h.get("isClosed"):
            cnt += 1

    if cnt >= 6:
        _tmp = ["Closed"]

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
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
    locator_domain = "https://www.bang-olufsen.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
