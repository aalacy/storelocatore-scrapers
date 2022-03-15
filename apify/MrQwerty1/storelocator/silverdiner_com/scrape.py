from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://silverdiner.squarespace.com/locations"

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='sqs-block-content' and ./h3]")

    for d in divs:
        location_name = "".join(d.xpath("./h3/text()")).strip()
        line = d.xpath("./h3/following-sibling::p[1]//text()")
        line = list(
            filter(
                None,
                [l.replace("\xa0", "").replace("\ufeff", "").strip() for l in line],
            )
        )
        full_adr = ", ".join(line)

        street_address = line.pop(0)
        if "Coming" in street_address:
            continue
        line = line.pop(0)
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        page_url = "".join(
            d.xpath(".//a[./strong[contains(text(), 'View More')]]/@href")
        )
        if page_url.startswith("/"):
            page_url = f"https://silverdiner.squarespace.com{page_url}"

        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        try:
            text = "".join(d.xpath(".//a[contains(@href, 'maps')]/@href"))
            latitude, longitude = text.split("ll=")[1].split("&")[0].split("%2C")
        except ValueError:
            latitude, longitude = "<MISSING>", "<MISSING>"

        hours = d.xpath(
            "p[./a[contains(@href, 'tel:')]]/following-sibling::p[1]/text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours) or SgRecord.MISSING

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
            raw_address=full_adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.silverdiner.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
