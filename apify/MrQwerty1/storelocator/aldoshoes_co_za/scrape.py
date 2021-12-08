import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_urls():
    urls = []
    r = session.get("https://www.aldoshoes.co.za/find-a-store/")
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var storesLayer =')]/text()"))
    text = text.split("var storesLayer =")[1].split("}]}];")[0] + "}]}]"
    js = json.loads(text)[0]["stores"]
    for j in js:
        urls.append(j.get("url"))

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    raw_address = " ".join(
        "".join(tree.xpath("//ul[@class='details']/li[1]/text()")).split()
    )
    street_address, city, state, postal = get_international(raw_address)
    country = "ZA"
    if state == "NA":
        state = SgRecord.MISSING
        country = "NA"
    elif "Botswana" in raw_address:
        city = "Gabrone"
        country = "BW"
    store_number = page_url.split("/")[-2].split("-")[-1]
    phone = "".join(
        tree.xpath("//span[contains(text(), 'Phone')]/following-sibling::text()")
    ).strip()
    if phone.count("0") == 10 or "Not" in phone:
        phone = SgRecord.MISSING

    try:
        text = "".join(tree.xpath("//a[contains(@href, 'daddr=')]/@href"))
        latitude, longitude = text.split("=")[-1].split(",")
    except:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country,
        phone=phone,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
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
    locator_domain = "https://www.aldoshoes.co.za/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
