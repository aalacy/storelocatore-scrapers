from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kfc.com.mt/"
    api_url = "https://www.kfc.com.mt/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//*[@class="locator-restaurant"]')
    for d in div:

        page_url = "https://www.kfc.com.mt/"
        location_name = (
            "".join(d.xpath('.//h3[@class="locator-restaurant__name"]/text()'))
            .replace("\n", "")
            .strip()
        )
        street_address = (
            "".join(
                d.xpath(
                    './/p[@class="locator-restaurant__phone"]/following-sibling::p[1]/text()'
                )
            )
            .replace("\r\n", "")
            .strip()
        )
        country_code = "MT"
        city = (
            "".join(
                d.xpath(
                    './/p[@class="locator-restaurant__phone"]/following-sibling::p[2]/text()'
                )
            )
            .replace("\r\n", "")
            .strip()
        )
        city = city.replace("Il-GÅ¼ira", "Il-Gżira")
        text = (
            "".join(d.xpath('.//p[@class="locator-restaurant__map"]/a/@href'))
            or "<MISSING>"
        )
        if text == "<MISSING>":
            text = (
                "".join(
                    d.xpath(
                        './/div[@class="locator-restaurant__embed-map"]/iframe/@src'
                    )
                )
                or "<MISSING>"
            )
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            try:
                latitude = text.split("q=")[1].split(",")[0]
                longitude = text.split("q=")[1].split(",")[1].split("&")[0]
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(d.xpath('.//p[@class="locator-restaurant__phone"]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                d.xpath('.//div[@class="locator-restaurant__opening-times"]//text()')
            )
            .replace("\r\n", "")
            .replace("Opening Times", "")
            .strip()
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
