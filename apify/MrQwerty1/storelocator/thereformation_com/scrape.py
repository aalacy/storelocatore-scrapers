from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from urllib import parse


def get_urls():
    r = session.get("https://www.thereformation.com/pages/stores")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='image-new-content-block__content-link']/@href")


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_data(page_url, sgw: SgWriter):
    if page_url.startswith("/"):
        page_url = f"https://www.thereformation.com{page_url}"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    lines = tree.xpath(
        "//div[@class='content-block content-block--hidden-for-small content-block--image-new content-block--show-divider-true']//text()"
    )
    lines = list(filter(None, [l.strip() for l in lines]))
    if not lines:
        return

    if "soon" in lines[-1].lower():
        return

    hours_index = 0
    for l in lines:
        if l.startswith("Hours:"):
            break
        hours_index += 1

    line = lines[1:hours_index]
    street_address = ", ".join(line[:-1]).replace(",,", ",")
    if "Mall" in street_address:
        street_address = street_address.split("Mall,")[1].strip()
    city = line[-1]
    state = "<MISSING>"
    postal = "<MISSING>"
    if city == "London":
        country_code = "GB"
    elif city == "North York":
        country_code = "CA"
    else:
        country_code = "US"

    try:
        phone = tree.xpath(
            "//div[@class='content-block content-block--hidden-for-small content-block--image-new content-block--show-divider-true']//a[contains(@href, 'tel:')]/@href"
        )[-1].replace("tel:+", "")
        phone = parse.unquote(phone).replace("\xa0", "")
    except IndexError:
        phone = "<MISSING>"
    text = "".join(
        tree.xpath(
            "//div[@class='content-block content-block--hidden-for-small content-block--image-new content-block--show-divider-true']//a[contains(@href, 'google')]/@href"
        )
    )
    latitude, longitude = get_coords_from_google_url(text)
    hours_of_operation = (
        ";".join(lines[hours_index + 1 : lines.index("Call:")]) or "Closed"
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
    locator_domain = "https://www.thereformation.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
