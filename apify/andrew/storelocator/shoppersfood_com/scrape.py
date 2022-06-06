from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.shoppersfood.com/"
    api_url = "https://www.shoppersfood.com/stores/search-stores.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//h2[text()="View Store by State"]/following-sibling::div//div[./a]/a'
    )
    for d in div:
        slug = "".join(d.xpath(".//@href")).split("?")[-1].strip()
        state_page_url = f"https://www.shoppersfood.com/stores/store-search-results.html?displayCount=18&{slug}"
        r = session.get(state_page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath("//li[@data-storeid]")
        for d in div:

            slug = "".join(d.xpath('.//a[text()="See Store Details"]/@href'))
            page_url = f"https://www.shoppersfood.com{slug}"
            location_name = (
                "".join(d.xpath('.//h2[@class="store-display-name h6"]/text()'))
                or "<MISSING>"
            )
            street_address = "".join(d.xpath('.//p[@class="store-address"]/text()'))
            ad = "".join(d.xpath('.//p[@class="store-city-state-zip"]/text()'))
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()
            country_code = "US"
            city = ad.split(",")[0].strip()
            store_number = "".join(d.xpath("./@data-storeid")) or "<MISSING>"
            latitude = "".join(d.xpath("./@data-storelat")) or "<MISSING>"
            longitude = "".join(d.xpath("./@data-storelng")) or "<MISSING>"
            phone = (
                "".join(d.xpath('.//p[@class="store-main-phone"]/span/text()'))
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(d.xpath('.//ul[@class="store-regular-hours"]/li//text()'))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split()).replace("Store Hours:", "").strip()
                or "<MISSING>"
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
                store_number=store_number,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=f"{street_address} {ad}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
