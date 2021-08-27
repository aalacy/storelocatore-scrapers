from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(
        "https://www.westfieldbank.com/search/location?q=&branch=Branch&submit=Go"
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//a[text()='View Location Details']/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath(
        "//p[./a[text()='Get Directions']]/preceding-sibling::p[1]//text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    phone = line.pop()
    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"

    text = "".join(tree.xpath("//a[text()='Get Directions']/@href"))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours = tree.xpath("//h6[text()='Lobby Hours']/following-sibling::p[1]/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours) or SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
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

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.westfieldbank.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
