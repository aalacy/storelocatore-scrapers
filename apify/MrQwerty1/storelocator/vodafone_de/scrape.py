from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    r = session.get("https://shops.vodafone.de/sitemap.xml")
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc/text()")
    for link in links:
        if link.count("/") == 4:
            urls.append(link)

    return urls


def get_data(page_url, sgw: SgWriter):
    try:
        r = session.get(f"{page_url}.json")
        j = r.json()["profile"]
    except:
        return

    location_name = j.get("name")
    a = j.get("address")

    street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
    city = a.get("city")
    state = a.get("region")
    postal = a.get("postalCode")
    country_code = a.get("countryCode")
    store_number = j.get("corporateCode")
    phone = j.get("mainPhone").get("display")
    latitude = j["yextDisplayCoordinate"]["lat"]
    longitude = j["yextDisplayCoordinate"]["long"]
    try:
        days = j["hours"]["normalHours"]
    except KeyError:
        days = []

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

            if start == "0":
                start = "1200"

            line = f"{day}:  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
        except IndexError:
            line = f"{day}:  Closed"

        _tmp.append(line)

    hours_of_operation = ";".join(_tmp)
    if (
        hours_of_operation.count("Closed") == 7
        or location_name.lower().find("closed") != -1
    ):
        hours_of_operation = "Closed"

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
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://vodafone.de/"
    session = SgRequests()

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
