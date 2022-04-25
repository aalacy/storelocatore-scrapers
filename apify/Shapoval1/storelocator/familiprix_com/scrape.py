import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent import futures


def get_urls():
    session = SgRequests()
    r = session.get(
        "https://familiprix-production.s3.amazonaws.com/sitemaps/pharmacies_sitemap.xml"
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), 'en/pharmacies')]/text()")


def get_data(url, sgw: SgWriter):
    locator_domain = "https://www.familiprix.com/en/"
    page_url = url
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = (
        "["
        + "".join(
            tree.xpath('//script[contains(text(), "openingHoursSpecification")]/text()')
        )
        + "]"
    )
    try:
        js = json.loads(block)
    except json.decoder.JSONDecodeError:
        return
    for j in js:
        ad = j.get("address")
        street_address = ad.get("streetAddress")
        city = ad.get("addressLocality")
        state = ad.get("addressRegion")
        postal = ad.get("postalCode")
        country_code = ad.get("addressCountry")
        location_name = j.get("name")
        phone = j.get("telephone")
        latitude = j.get("geo").get("latitude")
        longitude = j.get("geo").get("longitude")
        hours = j.get("openingHoursSpecification")
        tmp = []
        for h in hours:
            days = "".join(h.get("dayOfWeek")).split("/")[-1]
            opens = h.get("opens")
            closes = h.get("closes")
            line = f"{days} - {opens} : {closes}"
            if opens == closes:
                line = f"{days} - Closed"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
