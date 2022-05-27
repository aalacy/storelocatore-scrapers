from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//h2[text()='Locations & Hours']/following-sibling::table[1][@class='Table-Grid']//tr"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//h3/strong/text()")).strip()
        line = d.xpath(".//h4[1]/preceding-sibling::p//text()")
        line = list(filter(None, [l.strip() for l in line]))
        line = line[:-2]
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        phone = (
            d.xpath(".//p[contains(text(), 'Toll')]/text()")[0].split("Toll")[0].strip()
        )

        hours_of_operation = "".join(
            d.xpath(".//h4[contains(text(), 'Lobby')]/following-sibling::p[1]/text()")
        )
        if not hours_of_operation:
            hours_of_operation = " ".join(
                d.xpath(
                    ".//h4[contains(text(), 'Drive-Up')]/following-sibling::p/text()"
                )
            )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://chippewavalleybank.com/"
    page_url = "https://chippewavalleybank.com/Locations-Hours-ATMs"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
