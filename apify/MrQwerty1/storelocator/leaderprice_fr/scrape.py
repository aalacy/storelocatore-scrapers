import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(
        "https://www.leaderprice.fr/magasin/stores-sitemap.xml", headers=headers
    )
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div/@data-locations")).replace("&amp;#039;", "'")
    j = json.loads(text)[0]

    location_name = " ".join(tree.xpath("//h2[@itemprop='name']/text()")).strip()
    street_address = j.get("address")
    city = j.get("city")
    postal = j.get("cp")
    country_code = "FR"
    phone = j.get("phone")
    latitude = "".join(tree.xpath("//div/@data-lat"))
    longitude = "".join(tree.xpath("//div/@data-long"))

    _tmp = []
    hours = tree.xpath("//ul[@itemprop='openingHours']/li")
    for h in hours:
        day = "".join(h.xpath("./div[1]//text()")).strip()
        inter = "".join(h.xpath("./div[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
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
    locator_domain = "https://www.leaderprice.fr/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests(proxy_country="fr")
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
