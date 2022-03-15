from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    params = (("-token.S", ""),)

    data = {"miles": "5000", "ZipCode": "75022", "Submit": "Search"}
    r = session.post(
        "https://www.10boxcostplus.com/StoreLocator/Store_distance_S.las",
        headers=headers,
        params=params,
        data=data,
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//td/a[contains(@href, 'Store_Detail_S.las?L=')]/@href")


def get_data(page_url, sgw: SgWriter):
    page_url = page_url.replace("_Detail_S.las", "/")
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='row']/following-sibling::h3/text()")
    ).strip()
    line = tree.xpath("//p[@class='Address']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    store_number = page_url.split("L=")[1].split("&")[0]
    phone = tree.xpath("//p[@class='PhoneNumber']/a/text()")[0].strip()

    try:
        text = "".join(tree.xpath("//script[contains(text(), 'initializeMap')]/text()"))
        latitude, longitude = eval(text.split("initializeMap")[1].split(";")[0])
        if not latitude:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    hours_of_operation = ";".join(
        tree.xpath("//dt[text()='Hours of Operation:']/following-sibling::dd[1]/text()")
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=12) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.10boxcostplus.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.10boxcostplus.com",
        "Connection": "keep-alive",
        "Referer": "https://www.10boxcostplus.com/StoreLocator/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
