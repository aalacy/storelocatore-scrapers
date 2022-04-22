from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://salcobrand.cl/"
    api_url = "https://salcobrand.cl/content/servicios/mapa?current_store_id=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    last_page = (
        "".join(tree.xpath('//a[text()="Última"]/@href'))
        .split("page=")[1]
        .split("/")[0]
        .strip()
    )
    for i in range(1, int(last_page) + 1):
        page_url = (
            f"https://salcobrand.cl/content/servicios/mapa?current_store_id=1&page={i}"
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//li[@class="stores__pill"]')
        for d in div:

            street_address = (
                "".join(
                    d.xpath(
                        './/div[@class="stores__content stores__content--is-address"]/p/text()'
                    )
                )
                or "<MISSING>"
            )
            if street_address == "<MISSING>":
                continue
            state = (
                "".join(
                    d.xpath(
                        './/div[@class="stores__content stores__content--is-region"]/p/text()'
                    )
                )
                or "<MISSING>"
            )
            country_code = "CL"
            city = (
                "".join(
                    d.xpath(
                        './/div[@class="stores__content stores__content--is-county"]/p/text()'
                    )
                )
                or "<MISSING>"
            )
            try:
                latitude = (
                    "".join(
                        d.xpath(
                            './/div[@class="stores__content stores__content--is-map"]/a/@href'
                        )
                    )
                    .split("/")[-1]
                    .split(",")[0]
                    .strip()
                )
                longitude = (
                    "".join(
                        d.xpath(
                            './/div[@class="stores__content stores__content--is-map"]/a/@href'
                        )
                    )
                    .split("/")[-1]
                    .split(",")[1]
                    .strip()
                )
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/div[@class="stores__content stores__content--is-schedule"]/p/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=SgRecord.MISSING,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=SgRecord.MISSING,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=SgRecord.MISSING,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
