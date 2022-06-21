import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://sushishop.fr/"
    urls = [
        "https://www.sushishop.fr/sitemap_stores.xml",
        "https://www.sushishop.be/sitemap_stores.xml",
        "https://www.mysushishop.ch/sitemap_stores.xml",
        "https://www.sushishop.lu/sitemap_stores.xml",
        "https://www.mysushishop.co.uk/sitemap_stores.xml",
        "https://www.sushishop.it/sitemap_stores.xml",
        "https://www.sushishop.eu/sitemap_stores.xml",
        "https://www.sushiart.ae/sitemap_stores.xml",
        "https://www.sushiart.sa/sitemap_stores.xml",
    ]
    for url in urls:

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(url, headers=headers)
        tree = html.fromstring(r.content)
        div = tree.xpath("//url/loc")
        for d in div:

            page_url = "".join(d.xpath("./text()"))
            r = session.get(page_url, headers=headers)

            tree = html.fromstring(r.text)
            js_block = "".join(
                tree.xpath('//script[contains(text(), "streetAddress")]/text()')
            )
            js = json.loads(js_block)
            location_name = js.get("name") or "<MISSING>"
            a = js.get("address")
            street_address = a.get("streetAddress") or "<MISSING>"
            city = a.get("addressLocality") or "<MISSING>"
            state = a.get("addressRegion") or "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"
            country_code = a.get("addressCountry") or "<MISSING>"
            phone = js.get("telephone") or "<MISSING>"
            hours_of_operation = (
                " ".join(tree.xpath('//ul[@class="opening-hours__list"]/li//text()'))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            latitude = js.get("geo").get("latitude") or "<MISSING>"
            longitude = js.get("geo").get("longitude") or "<MISSING>"

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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
