from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    page_url = "https://www.pret.ch/en-ch/find-us"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='panel-body tabs-section']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='row']/h3[not(@class)]/text()")
        ).strip()
        line = d.xpath(
            ".//div[@class='row']/h3[not(@class)]/following-sibling::p[1]/text()"
        )
        phone = line.pop()

        raw_address = ", ".join(line)
        if "(" in raw_address:
            raw_address = raw_address.split("(")[0] + raw_address.split(")")[1].strip()

        zc = line.pop()
        postal = zc.split()[0]
        city = zc.replace(postal, "").split(",")[0].split("-")[0].strip()
        street_address = raw_address.split(f", {postal}")[0].replace(" ,", ",").strip()
        text = "".join(d.xpath(".//div/@data-position"))
        latitude, longitude = text.split(", ")
        hours_of_operation = d.xpath(".//h3/following-sibling::p[last()]/text()")[
            0
        ].strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="CH",
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
            phone=phone,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.pret.ch/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
