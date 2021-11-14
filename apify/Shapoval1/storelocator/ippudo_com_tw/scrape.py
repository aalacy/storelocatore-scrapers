from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ippudo.com.tw/"
    api_url = "https://www.ippudo.com.tw/branch/all/1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@id="page_s"]/option')
    for d in div:

        page_url = "".join(d.xpath(".//@value"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        block = tree.xpath('//div[@class="box"]')
        for b in block:
            location_name = "".join(b.xpath('.//h3[@itemprop="name"]/text()'))
            ad = (
                " ".join(
                    b.xpath('.//div[text()="【地址】"]/following-sibling::div[1]/text()')
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
            country_code = "TW"
            city = a.city or "<MISSING>"
            text = "".join(b.xpath('.//a[contains(@href, "maps")]/@href'))
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
                " ".join(
                    b.xpath('.//div[text()="【電話】"]/following-sibling::div[1]//text()')
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    b.xpath('.//div[text()="【營業時間】"]/following-sibling::div[1]//text()')
                )
                .replace("\n", "")
                .strip()
            )

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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
