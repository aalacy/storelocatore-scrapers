from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords(page_url):
    r = session.get(page_url)
    if r.status_code == 404:
        return SgRecord.MISSING, SgRecord.MISSING, False
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//iframe/@src"))
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    iscoming = False
    if "Coming" in "".join(tree.xpath("//h1/text()")):
        iscoming = True

    return latitude, longitude, iscoming


def get_uniq(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    line = tree.xpath("//div[./div/i[contains(@class, 'map')]]//text()")
    line = list(filter(None, [li.strip() for li in line]))
    line[0] = f"{line[0]}, {line[1]}"
    line.pop(1)
    return line


def fetch_data(sgw: SgWriter):
    api = "https://suncrestcare.com/location/"
    r = session.get(api)
    tree = html.fromstring(r.text)

    divs = tree.xpath(
        "//div[@class='g-block  size-33-3' and .//div[@class='g-mosaicgrid-image']]"
    )
    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='g-mosaicgrid-item-title']//text()")
        ).strip()
        page_url = "".join(d.xpath(".//div[@class='g-mosaicgrid-item-title']/a/@href"))
        if page_url.startswith("/"):
            page_url = f"https://suncrestcare.com{page_url}"
        line = d.xpath(".//div[@class='g-mosaicgrid-item-desc']/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if len(line) == 1:
            continue
        if line[0][0].isalpha():
            line.pop(0)
        if len(line) == 2:
            line = line.pop(0).split("\n")
            line[0] = f"{line[0].strip()}, {line[1]}"
            line.pop(1)

        if "pittsburgh" in page_url:
            line = get_uniq(page_url)

        street_address = line.pop(0)
        csz = line.pop(0).replace(",", "").split()
        postal = csz.pop()
        state = csz.pop()
        city = " ".join(csz)

        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        latitude, longitude, iscoming = get_coords(page_url)
        hours_of_operation = SgRecord.MISSING
        if iscoming:
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://suncrestcare.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
