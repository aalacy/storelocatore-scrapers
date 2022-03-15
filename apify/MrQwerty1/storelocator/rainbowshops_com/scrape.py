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
        tree = get_tree(f"https://stores.rainbowshops.com{region}")
        urls += tree.xpath("//div[@class='state-infobox-title']/a/@href")

    return urls


def get_urls():
    tree = get_tree("https://stores.rainbowshops.com/")
    regions = tree.xpath("//div[@class='state']/a/@href")

    return get_urls_from_regions(regions)


def get_data(slug, sgw: SgWriter):
    page_url = f"https://stores.rainbowshops.com{slug}"
    store_number = page_url.split("/")[-2]
    tree = get_tree(page_url)
    location_name = "".join(tree.xpath("//div[@id='main-content']/h1/text()")).strip()
    div = tree.xpath("//div[@role='main']")[0]
    line = div.xpath(".//div[@id='locdetails']//div[@class='loc-address']/div/text()")
    line = list(filter(None, [li.strip() for li in line]))

    street_address = ", ".join(line[:-1])
    csz = line.pop()
    city = csz.split(", ")[0]
    csz = csz.split(", ")[1]
    state, postal = csz.split()

    phone = "".join(
        div.xpath(".//div[@id='locdetails']//a[contains(@href, 'tel:')]/text()")
    ).strip()
    latitude = "".join(div.xpath(".//div/@data-lat"))
    longitude = "".join(div.xpath(".//div/@data-lng"))

    _tmp = []
    hours = div.xpath(".//div[@id='locdetails']//tr")
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
        country_code="US",
        store_number=store_number,
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
    locator_domain = "https://www.rainbowshops.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
