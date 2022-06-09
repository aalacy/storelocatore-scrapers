from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://kfc-ukraine.com"
    api_url = "https://www.kfc-ukraine.com/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="card"]')

    for d in div:

        page_url = "https://www.kfc-ukraine.com/stores"
        location_name = (
            "".join(d.xpath('.//h5[@class="card-title mainColor"]/text()'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(d.xpath('.//p[@class="card-text address"]/text()'))
            .replace("\n", "")
            .strip()
        )
        postal = ad.split(",")[-1].strip()
        country_code = "UA"
        city = ad.split(",")[-2].strip()
        if city.find("область") != -1:
            city = ad.split(",")[-3].strip()
        street_address = (
            ad.split(f", {city}")[0]
            .replace(', ТРЦ "Мегамолл"', "")
            .replace(", ТРК Victoria Gardens", "")
            .replace("Дом торговли", "")
            .strip()
        )
        store_number = "".join(d.xpath("./@data-id"))
        latitude = "".join(d.xpath("./@data-lat"))
        longitude = "".join(d.xpath("./@data-lng"))
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/td[text()="На винос - часи роботи:"]/following-sibling::td//text()'
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
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
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
