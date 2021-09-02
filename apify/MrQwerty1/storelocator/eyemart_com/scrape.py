from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://eyemart.com/landing-page/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(@href, '/stores/')]/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@class='storeInfo']/h2/text()")).strip()
    line = tree.xpath("//div[@class='storeInfo']/p/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]
    line = line[1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = page_url.split("/")[-1]
    phone = (
        "".join(
            tree.xpath("//div[@class='storeInfo']//span[@class='tel']/text()")
        ).strip()
        or "<MISSING>"
    )

    text = "".join(
        tree.xpath("//script[contains(text(), 'google.maps.LatLng')]/text()")
    )
    latitude = text.split('parseFloat("')[1].split('"')[0]
    longitude = text.split('parseFloat("')[-1].split('"')[0]

    _tmp = []
    days = tree.xpath("//div[@class='days']/p/text()")
    text = "".join(tree.xpath("//script[contains(text(), 'siteHour ?')]/text()"))
    times = eval(text.split("siteHour ?")[1].split(": [")[0])

    for d, t in zip(days, times):
        if d.strip():
            _tmp.append(f"{d.strip()} {t.strip()}")

    hours_of_operation = ";".join(_tmp).replace(": -", ": Closed") or SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
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
    locator_domain = "https://eyemart.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
