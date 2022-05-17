from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://stores.kohler.com/en/locations/experience-centers")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='ksslocationcards--store-link']/@href")


def get_data(slug, sgw: SgWriter):
    if slug.startswith("http"):
        page_url = slug
    else:
        page_url = f"https://stores.kohler.com{slug}"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//input[@id='Location']/@value"))
    street_address = "".join(tree.xpath("//input[@id='Address']/@value"))
    city = "".join(tree.xpath("//input[@id='City']/@value"))
    state = "".join(tree.xpath("//input[@id='State']/@value"))
    postal = "".join(tree.xpath("//input[@id='Zip']/@value"))
    store_number = "".join(tree.xpath("//input[@id='bpnumber']/@value")[0])
    phone = "".join(tree.xpath("//input[@id='Phone']/@value"))

    _tmp = []
    hours = tree.xpath("//div[@class='opening-time']/input")

    for h in hours:
        day = "".join(h.xpath("./@data-day"))
        time = "".join(h.xpath("./@data-time"))
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        store_number=store_number,
        country_code="US",
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
    locator_domain = "https://stores.kohler.com/en/locations/experience-centers"
    session = SgRequests()

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
