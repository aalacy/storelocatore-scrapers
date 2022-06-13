import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = set()
    for i in range(100):
        api = f"https://www.tegut.com/maerkte/marktsuche/seite/{i}.html?mktegut%5Baddress%5D=15000&mktegut%5Bradius%5D=3000&mktegut%5Bsubmit%5D=Markt%20suchen"
        r = session.get(api, headers=headers)
        tree = html.fromstring(r.text)
        slugs = tree.xpath("//h3[@class='h4 store-title float-left mr-1']/a/@href")

        check = f"https://www.tegut.com{slugs[0]}"
        if check in urls:
            break

        for slug in slugs:
            url = f"https://www.tegut.com{slug}"
            urls.add(url)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'GroceryStore')]/text()")
    ).strip()
    j = json.loads(text)

    location_name = j.get("name")
    a = j.get("address")
    street_address = a.get("streetAddress")
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    country_code = a.get("addressCountry")
    phone = j.get("telephone")
    store_number = j.get("branchCode")

    g = j.get("geo")
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    hours = j.get("openingHours") or []
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
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

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.tegut.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
