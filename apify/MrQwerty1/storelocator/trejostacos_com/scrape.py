from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.trejostacos.com/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[contains(@href, 'locations')]/following-sibling::span/a/@href"
    )


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_data(page_url, sgw: SgWriter):
    if page_url.startswith("/"):
        page_url = f"https://www.trejostacos.com{page_url}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//title/text()")[0].strip()
    line = tree.xpath("//h2/a[not(contains(@href, 'tel'))]/text()")
    line = list(filter(None, [l.strip() for l in line]))
    if not line:
        return
    if "Located" in line[0]:
        line.pop(0)

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    try:
        phone = (
            tree.xpath(
                "//h2/a[contains(@href, 'tel')]/@href|//h2[./a[contains(@href, 'google.com')]]/text()"
            )[0]
            .replace("tel:", "")
            .strip()
        )
        if phone == "(":
            phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/@href")).replace(
                "tel:", ""
            )
    except IndexError:
        phone = SgRecord.MISSING
    text = "".join(tree.xpath("//h2/a[not(contains(@href, 'tel'))]/@href"))
    latitude, longitude = get_coords_from_google_url(text)

    hours_of_operation = (
        " ".join(tree.xpath("//h2[./a]/following-sibling::h2[1]/text()"))
        or SgRecord.MISSING
    )

    if hours_of_operation == SgRecord.MISSING:
        hours_of_operation = " ".join(
            tree.xpath(
                "//h2/a[contains(@href, 'tel')]/text()|//h2[./a[contains(@href, 'google.com')]]/text()"
            )[1:]
        )

    row = SgRecord(
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
    locator_domain = "https://www.trejostacos.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
