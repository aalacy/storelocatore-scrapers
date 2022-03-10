from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.rumfatalagerinn.is"
    api_url = "https://www.rumfatalagerinn.is/thjonusta/opnunartimar/"
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="layout-item__full layout-card border__light"]')
    for d in div:

        page_url = "https://www.rumfatalagerinn.is/thjonusta/opnunartimar/"
        location_name = (
            "".join(d.xpath('.//h2[@class="font__header-secondary"]//text()'))
            .replace("\n", "")
            .strip()
        )
        location_name = " ".join(location_name.split())
        street_address = (
            "".join(
                d.xpath(
                    './/div[@class="layout__grid responsive no-padding half"]/p[1]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                d.xpath(
                    './/div[@class="layout__grid responsive no-padding half"]/p[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        postal = ad.split()[0].strip()
        country_code = "IS"
        city = ad.split()[1].strip()
        text = "".join(d.xpath('.//a[@class="map-button"]/@href'))
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
                d.xpath(
                    './/div[@class="layout__grid responsive no-padding half"]/p[1]/strong/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath(".//table//tr/td//text()")).replace("\n", "").strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        ad = f"{street_address} {ad}"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
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
