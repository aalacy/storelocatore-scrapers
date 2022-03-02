from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sansotei.com/"
    page_url = "https://www.sansotei.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./div/h3]")[1:]

    for d in div:
        info = d.xpath(".//span/text()")
        info = list(filter(None, [a.strip() for a in info]))
        for i in info:
            if "\u200b" in i:
                info.remove(i)

        location_name = "".join(info[0])
        street_address = "".join(info[1]).replace(",", "").strip()
        ad = "".join(info[2]).strip()
        phone_list = d.xpath('.//a[contains(@href, "tel")]/@href')

        phone = "".join(phone_list[-1]).replace("tel:", "").strip()
        state = ad.split(",")[1].strip()
        country_code = "Canada"
        city = ad.split(",")[0].strip()
        text = "".join(d.xpath('.//a[contains(@href, "/maps")]/@href'))
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
            " ".join(
                d.xpath(
                    './/span[@style="font-family:oswald-extralight,oswald,sans-serif;"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        tmpclz = "".join(
            d.xpath('.//span[contains(text(), "TEMPORARILY CLOSED")]/text()')
        )
        if tmpclz:
            hours_of_operation = "TEMPORARILY CLOSED"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
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
