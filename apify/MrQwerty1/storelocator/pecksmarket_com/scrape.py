from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://pecksmarket.shoptocook.com/locations/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='entry-content']/h2")
    for d in divs:
        location_name = "".join(d.xpath("./text()")).strip()
        line = d.xpath("./following-sibling::p[1]//text()")
        phone = line.pop()
        line.pop()
        csz = line.pop()
        city = csz.split(", ")[0]
        state, postal = csz.split(", ")[-1].split()
        street_address = line.pop()
        hours = d.xpath(
            "./following-sibling::p[2]/text()|./following-sibling::p[3]/text()"
        )
        hours = list(filter(None, [h.replace("\xa0", "").strip() for h in hours]))
        hours_of_operation = (
            " ".join(" ".join(hours).split()).strip().replace("pm ", "pm;")
        )
        text = "".join(d.xpath("./following-sibling::p[./a][1]/a/@href"))
        latitude, longitude = text.split("&ll=")[1].split("&")[0].split(",")

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
    locator_domain = "https://pecksmarket.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
