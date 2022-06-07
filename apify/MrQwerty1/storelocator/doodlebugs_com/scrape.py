from concurrent import futures
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_tree(url):
    r = session.get(url, headers=headers)
    return html.fromstring(r.text)


def get_urls_from_regions(regions):
    urls = []
    for region in regions:
        tree = get_tree(region)
        urls += tree.xpath(
            "//a[contains(@class, 'yellow-arrow') and contains(@href, '/location/')]/@href"
        )

    return urls


def get_urls():
    urls = []
    tree = get_tree("https://www.doodlebugs.com/")
    urls += tree.xpath(
        "//a[@class='yellow-btn' and contains(@href, '/location')]/@href"
    )
    regions = tree.xpath(
        "//a[@class='yellow-btn' and contains(@href, 'regional-page')]/@href"
    )
    urls += get_urls_from_regions(regions)

    return urls


def get_data(page_url, sgw: SgWriter):
    tree = get_tree(page_url)
    location_name = "".join(
        tree.xpath("//h1[@class='text-xs-center text-uppercase']/text()")
    ).strip()
    line = tree.xpath(
        "//p[@class='subheading-font subheading-size not-google-maps']/text()"
    )
    line = list(filter(None, [li.strip() for li in line]))

    street_address = ", ".join(line[:-1])
    csz = line.pop()
    city = csz.split(", ")[0]
    state = city.split()[-1]
    city = city.replace(state, "").strip()
    postal = csz.split(", ")[1]

    phone = "".join(tree.xpath("//div/@data-phone"))
    latitude = "".join(tree.xpath("//div/@data-lat"))
    longitude = "".join(tree.xpath("//div/@data-lng"))
    hours_of_operation = ";".join(
        tree.xpath(
            "//div[@class='row single-location-map js-doodle-locations']//p[contains(text(), 'Hours')]/text()"
        )
    )
    hours_of_operation = hours_of_operation.replace("Hours:", "").strip()

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


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.doodlebugs.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
