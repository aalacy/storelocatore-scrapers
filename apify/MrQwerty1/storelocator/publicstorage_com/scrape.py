import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.publicstorage.com/sitemap_plp.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@type='application/ld+json']/text()")).strip()
    if not text:
        return
    j = json.loads(text)["@graph"][0]

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    a = j.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    if len(postal) == 4:
        postal = f"0{postal}"
    country_code = a.get("addressCountry") or "<MISSING>"
    store_number = page_url.split("/")[-1]
    phone = j.get("telephone") or "<MISSING>"
    phone = phone.replace("+", "")
    g = j.get("geo") or {}
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"

    _tmp = []
    hours = j.get("openingHoursSpecification") or []
    for h in hours:
        day = ",".join(h.get("dayOfWeek"))
        start = h.get("opens")
        end = h.get("closes")
        _tmp.append(f"{day}: {start} - {end}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
    locator_domain = "https://www.publicstorage.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
