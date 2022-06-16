from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://www.mercantilrodrigues.com.br/lojas"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    blocks = tree.xpath("//div[@class='principal']/div")

    for b in blocks:
        state = "".join(b.xpath("./preceding-sibling::h2[1]//text()")).strip()
        divs = b.xpath(".//div[@class='view-content']/div")

        for d in divs:
            location_name = "".join(d.xpath(".//h3/text()|.//h4/text()")).strip()
            if "–" in location_name:
                city = location_name.split("–")[-1].strip()
            elif "-" in location_name:
                city = location_name.split("-")[-1].strip()
            else:
                city = location_name

            street_address = "".join(
                d.xpath(
                    ".//div[@class='views-field views-field-street']/span[@class='field-content']/text()"
                )
            ).strip()
            country_code = "BR"
            phone = "".join(
                d.xpath(
                    ".//div[@class='views-field views-field-field-televendas']/div[@class='field-content']/text()"
                )
            ).strip()

            if "|" in phone:
                phone = phone.split("|")[0].strip()
            if "-" in phone and phone.count("(") > 1:
                phone = phone.split("-")[0].strip()

            hours = d.xpath(".//div[contains(@class, 'horario')]//li/text()")
            hours = list(filter(None, [h.strip() for h in hours]))
            hours_of_operation = ";".join(hours)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mercantilrodrigues.com.br/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
