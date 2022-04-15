from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='place']")

    for d in divs:
        street_address = "".join(
            d.xpath(".//span[@property='streetAddress']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@property='addressLocality']/text()")).strip()
        state = "".join(d.xpath(".//span[@property='addressRegion']/text()")).strip()
        postal = d.xpath(".//span[@property='postalCode']/text()")[0].strip()
        country_code = "US"
        location_name = "".join(d.xpath(".//a/text()")).strip()
        phone = d.xpath(".//span[@property='postalCode']/text()")[1].strip()
        text = "".join(d.xpath("./@data-coords"))
        latitude, longitude = text.split(",")

        hours = d.xpath(
            ".//span[@property='postalCode'][last()]/following-sibling::text()"
        )[0]
        if "Main" in hours:
            hours = d.xpath(
                ".//span[@property='postalCode'][last()]/following-sibling::text()"
            )[1]
        hours_of_operation = " - ".join(hours.split(" - ")[1:])

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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://pioneer.bank/"
    page_url = "https://pioneer.bank/Contact-Us/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
