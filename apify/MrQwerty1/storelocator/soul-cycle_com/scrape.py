from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.soul-cycle.com/studios/all/partial/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='studio-link']/@href")


def clean_adr(text):
    if text.find("(") != -1:
        text = text.split("(")[0].strip()

    if text.find(",") != -1:
        lines = text.split(",")
        for line in lines:
            if line.strip()[0].isdigit():
                text = line.strip()
                break

    if text.find(":") != -1:
        lines = text.split(":")
        for line in lines:
            if line.strip()[0].isdigit():
                text = line.strip()
                break

    return text


def get_data(url, sgw: SgWriter):
    page_url = f"https://www.soul-cycle.com{url}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    d = tree.xpath("//div[@class='studio-location-container']")[0]
    location_name = "".join(tree.xpath("//h1[@class='studio-name']/@data-studio-name"))
    street_address = clean_adr(
        "".join(d.xpath(".//span[@itemprop='streetAddress']/text()"))
    )
    city = "".join(d.xpath(".//span[@itemprop='addressLocality']/text()"))
    state = "".join(d.xpath(".//span[@itemprop='addressRegion']/text()"))
    postal = (
        "".join(d.xpath(".//span[@class='studio-location']/text()"))
        .replace(",", "")
        .strip()
    )

    if len(postal) == 5:
        country_code = "US"
    else:
        if city == "London":
            country_code = "GB"
        else:
            country_code = "CA"

    phone = "".join(d.xpath(".//a[@itemprop='telephone']/text()"))
    store_number = "".join(d.xpath(".//a[@itemprop='telephone']/@data-studio-id"))

    line = "".join(
        tree.xpath("//script[contains(text(), 'var myLatlng')]/text()")
    ).split("\n")
    _tmp = ""
    for l in line:
        if l.find("var myLatlng =") != -1:
            _tmp = l
            break

    if _tmp:
        latitude = _tmp.split("(")[1].split(",")[0]
        longitude = _tmp.split("(")[1].split(",")[1].split(")")[0]
    else:
        latitude = SgRecord.MISSING
        longitude = SgRecord.MISSING

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
        hours_of_operation=SgRecord.MISSING,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.westfieldbank.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
