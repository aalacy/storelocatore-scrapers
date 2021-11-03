import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def translate(hours):
    hours = (
        hours.replace("à", "to")
        .replace("h00", ":00")
        .replace("Dimanche", "Sunday")
        .replace("Lundi", "Monday")
        .replace("Mardi", "Tuesday")
        .replace("Mercredi", "Wednesday")
        .replace("Jeudi", "Thursday")
        .replace("Vendredi", "Friday")
        .replace("Samedi", "Saturday")
    )
    return hours


def get_urls():
    r = session.get("https://www.bainmagique.com/qc-fr/liste-des-succursales/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='ColumnsWrapper']//a/@href")


def get_data(page_url, sgw: SgWriter):
    try:
        r = session.get(page_url)
        tree = html.fromstring(r.text)
    except:
        return
    text = "".join(tree.xpath("//script[@type='application/ld+json']/text()"))
    js = json.loads(text)

    location_name = "".join(tree.xpath("//div[@class=' bf-location-info']/h2/text()"))
    a = js.get("address")
    street_address = a.get("streetAddress")
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode") or ""
    country_code = a.get("addressCountry").get("name")
    if " " in postal:
        country_code = "CA"

    phone = "".join(tree.xpath("//a[@class='bf-li-item_phone']/text()")).strip()
    g = js.get("geo") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    _tmp = []
    hours = tree.xpath("//ul[@class='hours-wrap']/li")
    for h in hours:
        day = "".join(h.xpath("./span[@class='day']/text()")).strip()
        time = "".join(h.xpath("./span[@class='bf-hours']/text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp)
    if hours_of_operation.lower().count("closed") == 7:
        hours_of_operation = "Closed"

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

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.bainmagique.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
