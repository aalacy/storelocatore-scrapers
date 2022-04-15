from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.pollyspies.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='image_details']/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    if r.url == "https://www.pollyspies.com/locations/":
        return

    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//h2[text()='Address']/following-sibling::a/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"

    phone = "".join(
        tree.xpath("//h2[text()='Telephone']/following-sibling::p/text()")
    ).strip()
    text = "".join(
        tree.xpath("//script[contains(text(), 'single_location_lat')]/text()")
    )
    try:
        latitude = text.split("single_location_lat = ")[1].split(";")[0].strip()
        longitude = text.split("single_location_lng =")[1].split(";")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours_of_operation = " ".join(
        " ".join(tree.xpath("//div[@class='hours_block']//text()")).split()
    )

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
    locator_domain = "https://www.pollyspies.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
