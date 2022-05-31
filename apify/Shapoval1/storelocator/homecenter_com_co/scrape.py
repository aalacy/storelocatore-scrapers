from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.homecenter.com.co/"
    page_url = (
        "https://www.homecenter.com.co/homecenter-co/informacionadicional/tiendas"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="myBtnContainer"]/button[position() > 1]')
    for d in div:
        slug = "".join(d.xpath(".//@onclick")).split("('")[1].split("'")[0].strip()
        div = tree.xpath(
            f'//div[@class="column {slug}"]/div[./div/a[contains(@href, "maps")]]'
        )
        for d in div:

            location_name = "".join(d.xpath("./div[1]/strong[1]/text()"))
            street_address = (
                "".join(d.xpath("./div[2]/text()[1]")).replace("\n", "").strip()
            )
            country_code = "CO"
            city = slug.capitalize()
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
            hours_of_operation = (
                " ".join(d.xpath("./div[3]/div[1]//text()"))
                .replace("\n", "")
                .replace("\r", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            if hours_of_operation.count("Lunes") > 1:
                hours_of_operation = (
                    "Lunes " + hours_of_operation.split("Lunes")[1].strip()
                )

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
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
