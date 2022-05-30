from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sodimac.com.pe/"
    page_url = "https://www.sodimac.com.pe/sodimac-pe/content/a50055/nuestras-tiendas"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="cs"]/div')
    for d in div:
        slug = "".join(d.xpath(".//@id"))

        div = d.xpath('.//li[@class="detalleTienda text-center borderRadiusAll"]')
        for d in div:
            location_name = (
                "".join(d.xpath('.//span[@class="nombreTienda bold"]//text()'))
                .replace(":", "")
                .replace("\n", "")
                .strip()
            )
            location_name = " ".join(location_name.split())
            street_address = (
                "".join(d.xpath('.//span[@class="direccionTienda"]//text()'))
                .replace("\n", "")
                .strip()
            )
            street_address = " ".join(street_address.split())
            country_code = "PE"
            if slug == "tiendasLima":
                city = "Lima"
            else:
                city = location_name.split()[0].strip()
            text = "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
            try:
                if text.find("ll=") != -1:
                    latitude = text.split("ll=")[1].split(",")[0]
                    longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("@")[1].split(",")[0]
                    longitude = text.split("@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = (
                "".join(
                    tree.xpath('//*[contains(text(), "Venta Telefónica")]/span//text()')
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                "".join(
                    tree.xpath(
                        f'//span[./b[contains(text(), "HC {location_name}")]]/following-sibling::span[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if location_name == "Ate Vitarte":
                hours_of_operation = (
                    "".join(
                        tree.xpath(
                            '//span[./b[contains(text(), "HC Ate")]]/following-sibling::span[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
            if location_name == "Bellavista":
                hours_of_operation = (
                    "".join(
                        tree.xpath(
                            '//span[./b[contains(text(), "HC Bellevista")]]/following-sibling::span[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
            if location_name == "Open Plaza Angamos":
                hours_of_operation = (
                    "".join(
                        tree.xpath(
                            '//span[./b[contains(text(), "HC Angamos")]]/following-sibling::span[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
            if location_name == "Villa EL Salvador":
                hours_of_operation = (
                    "".join(
                        tree.xpath(
                            '//span[./b[contains(text(), "HC Villa El Salvador")]]/following-sibling::span[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
            if location_name == "Puruchuco Ate":
                hours_of_operation = (
                    "".join(
                        tree.xpath(
                            '//span[./b[contains(text(), "HC Puruchuco")]]/following-sibling::span[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
            if location_name == "Cajamarca Open Plaza":
                hours_of_operation = (
                    "".join(
                        tree.xpath(
                            '//span[./b[contains(text(), "HC Cajamarca")]]/following-sibling::span[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
            if location_name == "Trujillo Open Plaza":
                hours_of_operation = (
                    "".join(
                        tree.xpath(
                            '//span[./b[contains(text(), "HC Trujillo Open")]]/following-sibling::span[1]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
            if hours_of_operation.count("L-S") > 1:
                hours_of_operation = "L-S " + hours_of_operation.split("L-S")[1].strip()

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=SgRecord.MISSING,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
