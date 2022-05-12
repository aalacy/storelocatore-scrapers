from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(
        "https://www.aldoshoes.com/mx/en_MX/store-finder/results?latitude=&longitude=&q=*"
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//span[@class='store-maplink']/a/@href")


def get_data(slug, sgw: SgWriter):
    slug = slug.split("?")[0]
    page_url = f"https://www.aldoshoes.com{slug}"
    store_number = page_url.split("/")[-1]
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath("//script[contains(text(), 'var map;')]/text()"))
    location_name = "".join(tree.xpath("//h2/text()")).strip()
    street_address = (
        text.split("storeaddressline1 = '")[1]
        .split("';")[0]
        .encode("latin-1")
        .decode("unicode-escape")
        .strip()
    )
    city = (
        text.split("storeaddresstown = '")[1]
        .split("';")[0]
        .encode("latin-1")
        .decode("unicode-escape")
        .strip()
    )
    postal = (
        text.split("storeaddresspostalCode = '")[1]
        .split("';")[0]
        .replace("C.P.", "")
        .strip()
    )
    latitude = text.split("storelatitude = '")[1].split("';")[0].strip()
    longitude = text.split("storelongitude = '")[1].split("';")[0].strip()
    phone = "".join(
        tree.xpath(
            "//dt[./span[contains(text(), 'phone')]]/following-sibling::dd//text()"
        )
    ).strip()
    hours_of_operation = "".join(
        tree.xpath(
            "//dt[./span[contains(text(), 'Hours')]]/following-sibling::dd//text()"
        )
    ).strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="MX",
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
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
    locator_domain = "https://www.aldoshoes.com/mx/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
