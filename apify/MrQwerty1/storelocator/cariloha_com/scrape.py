from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_urls():
    r = session.get("https://www.cariloha.com/stores")
    tree = html.fromstring(r.text)

    return tree.xpath("//h3[@class='store-region']/following-sibling::p//a/@href")


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    if page_url != r.url:
        return

    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//h3[contains(text(), 'Address')]/following-sibling::p//text()")
    line = ", ".join(list(filter(None, [l.strip() for l in line])))

    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()

    if len(street_address) < 5:
        street_address = line.split(",")[0].strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode
    country_code = adr.country
    phone = (
        "".join(
            tree.xpath(
                "//h3[contains(text(), 'Contact')]/following-sibling::a[not(contains(@href, '@'))]/@href"
            )
        )
        .replace("tel:", "")
        .replace("mailto:", "")
        .strip()
    )
    latitude = "".join(tree.xpath("//div[@data-latitude]/@data-latitude"))
    longitude = "".join(tree.xpath("//div[@data-latitude]/@data-longitude"))

    _tmp = []
    tr = tree.xpath("//tr[@class='hours-row']")
    for t in tr:
        day = "".join(t.xpath("./td[1]//text()")).strip()
        time = "".join(t.xpath("./td[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp)

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


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.cariloha.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
