from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.yokesfreshmarkets.com/stores")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='viewstore']/a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@class='title']/text()")).strip()
    street_address = "".join(tree.xpath("//div[@class='address']//em/text()")).strip()
    line = "".join(tree.xpath("//span[@class='address-city']/text()")).strip()
    city = line.split(",")[0].strip()
    line = line.replace(city, "").replace(",", "")
    state = line.split()[0].replace(".", "")
    postal = line.split()[1]
    phone = "".join(tree.xpath("//div[@class='field-pharmacy-phone']/text()")).strip()
    hours_of_operation = " ".join(
        "".join(
            tree.xpath(
                "//h3[contains(text(), 'Pharmacy Hours')]/following-sibling::div[1]/ul//text()"
            )
        ).split()
    ).replace("pm ", "pm;")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        phone=phone,
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
    locator_domain = "https://www.yokesfreshmarkets.com/#pharmacy"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
