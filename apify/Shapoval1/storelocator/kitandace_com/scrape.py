from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kitandace.com"
    api_url = "https://www.kitandace.com/us/en/shoplocations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="js-store-item stores-list__item"]')

    for d in div:
        ft = "".join(d.xpath('.//div[@class="stores-data"]/p[1]/a/@href'))
        if ft.find("CLOSED") != -1 or ft.find("coming soon") != -1:
            continue
        slug = "".join(d.xpath('.//a[@class="button simple rare"]/@href'))
        latitude = "".join(d.xpath(".//@data-storelat"))
        longitude = "".join(d.xpath(".//@data-storelng"))
        page_url = f"{locator_domain}{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        ad = (
            "".join(tree.xpath('//div[@class="store-info store-info__address"]/text()'))
            .replace("\n", " ")
            .replace("The Village at Park Royal,", "")
            .strip()
        )
        if ad.find("closed") != -1:
            continue
        street_address = ad.split(",")[0].strip()
        phone = (
            "".join(
                tree.xpath('//a[@class="store-info store-info__phone"]/text()')
            ).strip()
            or "<MISSING>"
        )
        state = ad.split(",")[2].split()[0].strip()
        postal = " ".join(ad.split(",")[2].split()[1:]).strip()
        country_code = "CA"
        city = ad.split(",")[1].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[text()="Hours"]/following-sibling::table[@class="store-schedule"]//tr/td//text()'
                )
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
