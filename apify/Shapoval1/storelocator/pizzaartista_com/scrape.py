from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pizzaartista.com/"
    api_url = "https://pizzaartista.com/contact-us/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[./a[text()="Contact Us"]]/following-sibling::li/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//a[contains(@href, "maps")]')
        for d in div:

            location_name = (
                " ".join(tree.xpath("//h1//text()")).replace("\n", "").strip()
            )
            location_name = " ".join(location_name.split())
            ad = " ".join(d.xpath("./text()")).replace("\n", "").strip()
            ad = " ".join(ad.split())
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = a.city or "<MISSING>"
            phone = (
                "".join(d.xpath('.//following::a[contains(@href, "tel")][1]//text()'))
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/following::p[./strong[text()="Hours"]][1]/text() | .//following::p[contains(text(), "Hours:")]/text()'
                    )
                )
                .replace("\n", "")
                .replace("Hours:", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    "".join(
                        tree.xpath(
                            f'//a[contains(text(), "{street_address}")]/following-sibling::text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if hours_of_operation.find("Open") != -1:
                hours_of_operation = hours_of_operation.split("Open")[1].strip()

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
