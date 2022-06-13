import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    r = session.get("https://www.landmarktheatres.com/?portal")
    tree = html.fromstring(r.text)
    aa = tree.xpath("//a[@class='accordion-region-link']")
    for a in aa:
        _id = "".join(a.xpath("./@data-accordion-region-id"))
        region = "".join(a.xpath("./@data-accordion-region-link"))
        r = session.get(f"https://www.landmarktheatres.com/api/CinemasByRegion/{_id}")
        js = r.json()
        for j in js:
            slug = j.get("FriendlyName")
            urls.append(f"https://www.landmarktheatres.com/{region}/{slug}/info")

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//span[@class='header-theatre-location']/text()")
    ).strip()
    line = "".join(
        tree.xpath("//div[@class='header-theatre-group-middle']/a/text()")
    ).strip()
    street_address = line.split(",")[0].strip()
    city = line.split(",")[-3].strip()
    state = line.split(",")[-2].strip()
    postal = line.split(",")[-1].strip()

    if "." in state:
        city = "Washington D.C."
        state = "WA"

    try:
        phone = tree.xpath("//p[@class=' ta_c']/text()")[-2].strip() or "<MISSING>"
    except IndexError:
        phone = SgRecord.MISSING

    div = "".join(tree.xpath("//div[@data-map]/@data-map"))
    j = json.loads(div)
    latitude = j.get("lat")
    longitude = j.get("lng")
    hours_of_operation = SgRecord.MISSING
    if tree.xpath("//strong[contains(text(), 'COMING SOON')]"):
        hours_of_operation = "Coming Soon"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=str(latitude),
        longitude=str(longitude),
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.landmarktheatres.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
