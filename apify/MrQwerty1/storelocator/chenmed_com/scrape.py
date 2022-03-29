from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_tree(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)

    return tree


def get_urls():
    urls = []
    start_urls = [
        "https://www.jencaremed.com/find-a-location",
        "https://www.chenmedicalcenters.com/find-a-location",
        "https://www.dedicated.care/find-a-location",
    ]
    for u in start_urls:
        tree = get_tree(u)
        urls += tree.xpath("//a[@class='results-list-item__link-wrap']/@href")

    return urls


def get_hoo(url):
    tree = get_tree(url)
    hours = " ".join(
        "".join(
            tree.xpath("//h6[contains(text(), 'Hours')]/following-sibling::p/text()")
        ).split()
    )

    return hours


def get_data(api, sgw: SgWriter):
    tree = get_tree(api)
    divs = tree.xpath("//div[@class='location-list-item']")

    for d in divs:
        location_name = "".join(d.xpath(".//span[@itemprop='name']/text()")).strip()
        slug = "".join(d.xpath(".//a/@href"))
        root = api.split("/find-a-location/")[0].replace("/orlando", "")
        page_url = f"{root}{slug}"
        street_address = "".join(
            d.xpath(".//span[@itemprop='streetAddress']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
        state = "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
        postal = "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
        country_code = "US"
        phone = "".join(d.xpath(".//span[@itemprop='telephone']/text()")).strip()

        text = "".join(d.xpath("./@data-geolocation"))
        try:
            latitude, longitude = text.split(",")
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        if "coming" in page_url or "-moving" in page_url:
            hours_of_operation = "Coming Soon"
        else:
            hours_of_operation = get_hoo(page_url)

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
    locator_domain = "https://www.chenmed.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
