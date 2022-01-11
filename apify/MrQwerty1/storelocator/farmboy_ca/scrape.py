from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.farmboy.ca/stores-sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).strip()
    ad = (
        "".join(tree.xpath("//div[@class='loc__address']/p/text()")).strip().split(", ")
    )
    if len(ad) == 1:
        return

    raw_address = ", ".join(ad)
    postal = ad.pop()
    state = ad.pop()
    city = ad.pop()
    street_address = ", ".join(ad)
    if "canada" in street_address.lower():
        street_address = street_address.split(", ")[0]
    phone = "".join(tree.xpath("//div[@class='loc__contact']//a/text()")).strip()
    hours_of_operation = (
        " ".join(tree.xpath("//ul/li/span//text()"))
        .replace("(Today) ", "")
        .replace("PM ", "PM; ")
        .replace("\n", "")
        .strip()
    )

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="CA",
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.farmboy.ca/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
