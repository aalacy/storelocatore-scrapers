import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox


session = SgRequests()


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bravissimo.com/"
    api_url = "https://www.bravissimo.com/shops/all/"
    with SgFirefox() as driver:
        driver.get(api_url)
        a = driver.page_source
        tree = html.fromstring(a)
        div = tree.xpath('//a[@class="c-section-nav__label u-block-link"]')
        for d in div:
            slug = "".join(d.xpath(".//@href"))
            page_url = f"https://www.bravissimo.com{slug}"
            with SgFirefox() as driver:
                driver.get(page_url)
                a = driver.page_source
                tree = html.fromstring(a)
                js_block = "".join(
                    tree.xpath('//script[@type="application/ld+json"]/text()')
                )
                js = json.loads(js_block)
                location_name = (
                    "".join(
                        tree.xpath('//h1[contains(@class, "c-bandeau__title")]//text()')
                    )
                    .replace("\n", "")
                    .strip()
                    or "<MISSING>"
                )
                location_type = js.get("@type") or "<MISSING>"
                b = js.get("address")
                street_address = b.get("streetAddress") or "<MISSING>"
                state = b.get("addressRegion") or "<MISSING>"
                postal = b.get("postalCode") or "<MISSING>"
                if postal == "NY 10012":
                    state = str(postal).split()[0].strip()
                    postal = str(postal).split()[1].strip()
                country_code = b.get("addressCountry") or "<MISSING>"
                city = b.get("addressLocality") or "<MISSING>"
                latitude = js.get("geo").get("latitude") or "<MISSING>"
                longitude = js.get("geo").get("longitude") or "<MISSING>"
                phone = js.get("telephone") or "<MISSING>"
                hours_of_operation = js.get("openingHours") or "<MISSING>"
                tmpcls = "".join(
                    tree.xpath('//*[contains(text(), "Temporarily")]/text()')
                )
                if tmpcls:
                    hours_of_operation = "Temporarily Closed"

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
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
