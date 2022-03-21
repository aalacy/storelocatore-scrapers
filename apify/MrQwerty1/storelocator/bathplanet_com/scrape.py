from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.bathplanet.com/sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath(
        "//loc[contains(text(), '/locator/') and not(contains(text(), '/r-')) and not(text()='https://www.bathplanet.com/locator/')]/text()"
    )


def get_coords(text):
    try:
        return text.split("/@")[1].split(",")[:2]
    except IndexError:
        return SgRecord.MISSING, SgRecord.MISSING


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@itemprop='address']/h1/text()")).strip()
    street_address = (
        "".join(tree.xpath("//span[@itemprop='streetAddress']/text()"))
        .replace("...", "")
        .replace("-", "")
        .strip()
    )
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    country_code = "US"
    if len(postal) > 5:
        country_code = "CA"
    phone = "".join(tree.xpath("//p[@class='phone']//text()")).strip()
    text = "".join(tree.xpath("//div[@itemprop='address']//a/@href"))
    latitude, longitude = get_coords(text)
    hours_of_operation = " ".join(
        "".join(
            tree.xpath("//h5[text()='Hours']/following-sibling::p[1]//text()")
        ).split()
    )

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
    locator_domain = "https://www.bathplanet.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
