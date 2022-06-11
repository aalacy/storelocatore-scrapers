from lxml import html
from concurrent import futures
from datetime import datetime
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address


def get_urls():
    r = session.get("https://www.beatone.co.uk/bars")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='inner-item']/@href")


def get_data(url, sgw):
    page_url = f"https://www.beatone.co.uk/{url}"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1/text()")[1].strip()
    line = " ".join(tree.xpath("//ul[@class='menu vertical address']/li/text()"))
    adr = parse_address(International_Parser(), line)

    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode or "<MISSING>"
    if postal == "<MISSING>":
        postal = " ".join(street_address.split()[-2:])
        street_address = street_address.replace(postal, "").strip()
    country_code = "GB"
    phone = "".join(
        tree.xpath("//ul[@class='menu vertical']//a[contains(@href, 'tel')]//text()")
    ).strip()

    try:
        text = "".join(tree.xpath("//script[contains(text(), 'new H.Map(')]/text()"))
        text = text.split("center: ")[1].split("});")[0].strip()
        lat, lng = "lat", "lng"
        a = eval(text)
        latitude = a.get(lat)
        longitude = a.get(lng)
    except:
        latitude = SgRecord.MISSING
        longitude = SgRecord.MISSING

    _tmp = []
    divs = tree.xpath("//div[@class='opening-times']/div[./span]")
    for d in divs:
        day = "".join(d.xpath("./span/text()")).strip()
        time = "".join(d.xpath("./text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = (
        ";".join(_tmp).replace("Today", datetime.today().strftime("%A")) or "<MISSING>"
    )
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
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.beatone.co.uk/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
