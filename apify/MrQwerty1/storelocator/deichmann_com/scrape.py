from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    locator_domain = "https://deichmann.com/"
    gl_api_url = "https://stores.deichmann.com/index.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(gl_api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="countrydropdown"]/li/a')
    for d in div:
        slug = "".join(d.xpath(".//@href")).replace("index.html", "")
        api_url = f"{slug}assets/locations.json"
        r = session.get(api_url, headers=headers)
        js = r.json()
        for j in js:
            slug_page_url = j.get("url")
            page_url = f"{slug}{slug_page_url}"
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            ad = (
                " ".join(
                    tree.xpath(
                        '//section[@class="section section--filial-main-info"]//div[@class="filial"]//p[@class="filial__address"]/b/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            ad = " ".join(ad.split())
            location_name = "".join(tree.xpath("//h1/text()[1]")) or "<MISSING>"
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            if (
                street_address == "<MISSING>"
                or street_address.isdigit()
                or len(street_address) < 5
            ):
                street_address = ad
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            city = a.city or "<MISSING>"
            country_code = "".join(
                tree.xpath('//li[@class="breadcrumb__country"]/a/text()')
            )
            latitude = (
                "".join(
                    tree.xpath(
                        '//section[@class="section section--filial-main-info"]//span/@latitude'
                    )
                )
                or "<MISSING>"
            )
            longitude = (
                "".join(
                    tree.xpath(
                        '//section[@class="section section--filial-main-info"]//span/@longitude'
                    )
                )
                or "<MISSING>"
            )
            phone = "".join(
                tree.xpath(
                    '//section[@class="section section--filial-main-info"]//div[@class="filial"]//a[contains(@href, "tel")]/text()'
                )
            )
            hours_of_operation = (
                " ".join(tree.xpath('//ul[@id="business-hours"]/li//text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            cls = "".join(
                tree.xpath(
                    '//p[@class="filial__time filial__time_close closed_dop360"]//text()'
                )
            )
            if cls:
                hours_of_operation = "Closed"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
