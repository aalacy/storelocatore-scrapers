from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://locations.famsafurniture.com/store-list/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//h3/following-sibling::div//a/@href")


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_data(slug, sgw: SgWriter):
    page_url = f"https://locations.famsafurniture.com{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//div[@id='tab-address']//h5[a]//text()")
    line = list(filter(None, [li.strip() for li in line]))
    phone = line.pop()
    if ":" in phone:
        phone = phone.split(":")[-1].strip()
        line.pop()

    if "Inside" in line[0]:
        line.pop(0)

    csz = line.pop()
    street_address = ", ".join(line)
    city, sz = csz.split(", ")
    state, postal = sz.split()
    country_code = "US"

    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)

    _tmp = []
    hours = tree.xpath("//table[contains(@class, 'hours')]//tr")
    for h in hours:
        day = "".join(h.xpath("./td[1]//text()")).strip()
        inter = "".join(h.xpath("./td[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

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
    locator_domain = "https://famsafurniture.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
