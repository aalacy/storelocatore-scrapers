from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://superkingmarkets.com/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//h4[contains(text(), 'Stores')]/following-sibling::div//a/@href"
    )


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        return "", ""

    return latitude, longitude


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        return "", ""

    return latitude, longitude


def get_data(url, sgw: SgWriter):
    page_url = f"https://superkingmarkets.com{url}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h2[@class='store_name']/text()")).strip()
    line = tree.xpath("//div[@class='desktop_store_details']//p/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line.pop(0)
    csz = line.pop(0)
    city = csz.split(",")[0].strip()
    csz = csz.split(",")[1].strip()
    state = csz.split()[0]
    postal = csz.split()[1]
    day = "".join(
        tree.xpath("//div[@class='desktop_store_details']//p/strong[1]/text()")
    ).strip()
    inter = line.pop(0)
    hours_of_operation = f"{day} {inter}"
    phone = (
        "".join(
            tree.xpath(
                "//div[@class='desktop_store_details']//p/strong[last()]/following-sibling::text()|//div[@class='desktop_store_details']//p/a/text()"
            )
        )
        .replace(":", "")
        .strip()
    )
    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    if "embed" in text:
        latitude, longitude = get_coords_from_embed(text)
    else:
        latitude, longitude = get_coords_from_google_url(text)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
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
    locator_domain = "https://superkingmarkets.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
