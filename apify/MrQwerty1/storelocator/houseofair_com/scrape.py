import ssl
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgChrome


def get_tree(url):
    r = session.get(url)
    return html.fromstring(r.text)


def get_rendered_tree(url):
    with SgChrome() as fox:
        fox.get(url)
        source = fox.page_source

    return html.fromstring(source)


def get_urls():
    tree = get_tree("https://houseofair.com/locations/")
    return tree.xpath("//h3[@class='topspace0']/a/@href")


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def get_hoo(url):
    tree = get_tree(url)
    hours = tree.xpath(
        "//h2[contains(text(), 'Hours') or contains(text(), 'HOURS')]/following-sibling::ul[1]/li/text()"
    )
    hours = list(filter(None, [h.replace(" CT", "").strip() for h in hours]))

    return ";".join(hours)


def get_poland(page_url, sgw: SgWriter):
    tree = get_tree(page_url)
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    lines = tree.xpath(
        "//div[./img[contains(@src, 'web_blue')]]/following-sibling::div//text()"
    )
    lines = list(filter(None, [line.strip() for line in lines]))
    street_address = lines.pop(0).replace(",", "")
    postal, city = lines.pop(0).split(", ")[0].split()
    location_name = f"{city}, Poland"
    phone = "".join(set(tree.xpath("//a[contains(@href, 'tel:')]/text()"))).strip()
    hours = tree.xpath(
        "//div[contains(text(), 'ADRES')]/following-sibling::div//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours[hours.index("Godziny otwarcia") + 1 :])

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="PL",
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    for page_url in urls:
        if page_url.startswith("/"):
            page_url = f"https://houseofair.com{page_url}"

        if ".pl" in page_url:
            page_url = "http://www.houseofair.pl/kontakt"
            get_poland(page_url, sgw)
            continue

        tree = get_rendered_tree(page_url)
        _id = "".join(
            tree.xpath(
                "//strong[contains(text(), 'Address')]/following-sibling::a/@data-target"
            )
        ).replace("#", "")
        lines = tree.xpath(
            "//strong[contains(text(), 'Address')]/following-sibling::a/text()"
        )
        street_address = lines.pop(0)
        city, sz = lines.pop(0).split(", ")
        state, postal = sz.split()
        location_name = f"{city}, {state}"
        phone = "".join(
            tree.xpath(
                "//strong[contains(text(), 'Phone')]/following-sibling::a/text()"
            )
        )
        text = "".join(tree.xpath(f"//div[@id='{_id}']//iframe/@src"))
        latitude, longitude = get_coords_from_embed(text)

        url = "".join(set(tree.xpath("//a[@title='About']/@href")))
        hours_of_operation = get_hoo(url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    ssl._create_default_https_context = ssl._create_unverified_context
    locator_domain = "https://houseofair.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
