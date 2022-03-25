from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://nespresso.com.pa"
    api_urls = [
        "https://nespresso.com.pa/tiendas/",
        "https://nespresso.com.do/tiendas/",
    ]
    for api_url in api_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="principal_html"]')
        for d in div:

            page_url = api_url
            location_name = "".join(d.xpath(".//h3/text()"))
            ad = (
                "".join(
                    d.xpath(
                        './/p[./strong[text()="Direccion:"]]/following-sibling::p[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = api_url.split("com.")[1].split("/")[0].upper().strip()
            city = a.city or "<MISSING>"
            phone = (
                "".join(
                    d.xpath(
                        './/p[./strong[text()="Telefono:"]]/following-sibling::p[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            if phone.find(" - ") != -1:
                phone = phone.split(" - ")[0].strip()
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/p[./strong[text()="Telefono:"]]/following-sibling::p[1]/following-sibling::p//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            ) or "<MISSING>"
            if hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    " ".join(
                        d.xpath(
                            './/p[./strong[text()="Direccion:"]]/following-sibling::p[1]/following-sibling::p//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                ) or "<MISSING>"
            hours_of_operation = " ".join(hours_of_operation.split())

            row = SgRecord(
                locator_domain=locator_domain,
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
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
