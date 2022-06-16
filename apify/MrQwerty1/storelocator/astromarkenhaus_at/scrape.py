from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//iframe/@src"))
    try:
        return text.split("q=")[1].split("&")[0].split(",")
    except IndexError:
        return SgRecord.MISSING, SgRecord.MISSING


def fetch_data(sgw: SgWriter):
    r = session.get(locator_domain)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='contact']")
    for d in divs:
        location_name = "".join(d.xpath(".//h5/a/text()")).strip()
        page_url = "".join(d.xpath(".//h5/a/@href"))
        store_number = page_url.split("/")[-1]
        raw_address = "".join(d.xpath(".//h5/following-sibling::text()[1]")).strip()
        line = raw_address.split(", ")
        street_address = line.pop(0)
        csz = line.pop(0)
        postal = csz.split()[0]
        city = csz.replace(postal, "").strip()
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        latitude, longitude = get_coords(page_url)
        hours = d.xpath(".//a[contains(@href, 'mailto:')]/following-sibling::text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="AT",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://astromarkenhaus.at/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
