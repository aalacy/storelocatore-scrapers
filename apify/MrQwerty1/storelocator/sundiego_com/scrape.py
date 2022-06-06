from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[contains(@class, 'flex-grid__item flex-grid__item--50 flex-grid__item')]"
    )

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='rte--block rte--strong']/text()")
        ).strip()
        line = d.xpath(".//div[@class='rte--block']//text()")
        line = list(filter(None, [li.strip() for li in line]))

        hours_of_operation = line.pop().replace(" / ", ";")
        line.pop()  # remove email
        phone = line.pop().lower().replace("phone", "").replace(":", "").strip()
        raw_address = ", ".join(line)
        a = raw_address.split(", ")
        state = SgRecord.MISSING
        postal = a.pop()
        if " " in postal:
            state, postal = postal.split()
        city = a.pop()
        street_address = ", ".join(a)
        country_code = "US"

        text = "".join(d.xpath(".//a/@href"))
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        if "/@" in text:
            latitude, longitude = text.split("/@")[1].split(",")[:2]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://sundiego.com/"
    page_url = "https://sundiego.com/pages/sun-diego-locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
