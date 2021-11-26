from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("http://www.mosburger.com.au/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='btn_more_details']/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h3[@itemprop='name']/text()")).strip()
    street_address = "".join(
        tree.xpath("//div[@class='section_store_address_address']/text()")
    ).strip()
    phone = "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()
    city = "".join(
        tree.xpath("//span[@class='section_store_address_suburb']/text()")
    ).strip()
    state = "".join(
        tree.xpath("//span[@class='section_store_address_state']/text()")
    ).strip()
    postal = "".join(
        tree.xpath("//span[@class='section_store_address_postcode']/text()")
    ).strip()
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat"))
    longitude = "".join(tree.xpath("//div[@data-lng]/@data-lng"))
    text = "".join(
        tree.xpath("//div[@class='section_store_address_building_shop']/text()")
    )
    store_number = text.split()[1].replace(",", "").strip()

    _tmp = []
    hours = tree.xpath("//div[@class='div_30 section_date colour_black']")
    for h in hours:
        day = "".join(h.xpath("./text()")).strip()
        inter = "".join(h.xpath("./following-sibling::div[1]/text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="AU",
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
    locator_domain = "http://www.mosburger.com.au/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "http://www.mosburger.com.au/locations/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
