from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@id, 'map-info-home-map-')]")

    for d in divs:
        location_name = "".join(d.xpath("./preceding-sibling::a[1]/h3/text()")).strip()
        raw_address = "".join(
            d.xpath(".//div[@class='home-map__text rte']/p[1]/text()")
        ).strip()

        if "*" in raw_address:
            raw_address = raw_address.split("*")[0]
        city = raw_address.split(",")[-1].strip()
        street_address = ",".join(raw_address.split(",")[:-1])
        country_code = "IL"
        hours_of_operation = ";".join(
            d.xpath(".//div[@class='home-map__sub-text u-small rte']/p//text()")[1:]
        ).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code=country_code,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://max-brenner.co.il/"
    page_url = "https://max-brenner.co.il/pages/branches"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
