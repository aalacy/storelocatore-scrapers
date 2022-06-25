from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(locator_domain, headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//li[@class='LocationsDropdown-locationItem']/div/a[@class='RestaurantCard']/@href"
    )


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    if r.status_code != 200:
        return
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath(
        "//p[@class='RestaurantInfo-hours']/a/text()|//p[@class='RestaurantInfo-hours']/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))

    if len(line) == 1:
        street_address = SgRecord.MISSING
        city = line[0].split(",")[0].strip()
        state = line[0].split(",")[1].strip()
        postal = SgRecord.MISSING
    else:
        street_address = line[0]
        city = line[1].split(",")[0].strip()
        state = line[1].split(",")[1].strip()
        if "BC " in state:
            state = state.replace("BC ", "")
        postal = line[-1]

    country_code = "CA"
    phone = "".join(
        tree.xpath(
            "//p[@class='RestaurantInfo-phone']/a[contains(@href, 'tel')]/text()"
        )
    ).strip()
    latitude = "".join(
        tree.xpath("//meta[@property='place:location:latitude']/@content")
    )
    longitude = "".join(
        tree.xpath("//meta[@property='place:location:longitude']/@content")
    )

    if "." not in latitude:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    hours_of_operation = " ".join(
        ";".join(tree.xpath("//meta[@itemprop='openingHours']/@content")).split()
    )

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
    locator_domain = "https://www.tacofino.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
