from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honolulucookie.com/"
    page_url = "https://www.honolulucookie.com/content/store-locations.asp"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h3/following-sibling::ul[./li/a[contains(@href, "maps")]]')
    for d in div:

        location_name = "".join(d.xpath("./li[1]//text()"))
        street_address = (
            " ".join(
                d.xpath(
                    './li[contains(text(), "Ph:")]/preceding-sibling::li[1]/preceding-sibling::li[text()]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                d.xpath(
                    './li[contains(text(), "Ph:")]/preceding-sibling::li[1]//text()'
                )
            )
            .replace("Ph:", "")
            .strip()
        )
        if ad.find("(") != -1:
            ad = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        if ad != "<MISSING>":
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()
        text = "".join(d.xpath("./li[1]/a/@href"))
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
            "".join(d.xpath('./li[contains(text(), "Ph:")]/text()'))
            .replace("Ph:", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './li[@class="callout-text"]/strong//text() | ./li[./span[contains(text(), "TEMPO")]]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {ad}".replace("<MISSING>", "").strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
