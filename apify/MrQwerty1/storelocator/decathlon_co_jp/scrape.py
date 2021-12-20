from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(
        tree.xpath('//script[contains(text(), "var storeLocalisation")]/text()')
    ).split("redirection:")[1:]
    for d in div:
        slug = d.split("hours")[0].replace('"', "").replace(",", "").strip()
        page_url = f"https://www.decathlon.co.jp{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath('//h1[@class="store-information-bigTitle"]/text()')
        )
        ad = (
            " ".join(
                tree.xpath(
                    '//i[@class="fas fa-map-marker-alt"]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state
        postal = a.postcode
        country_code = "JP"
        city = a.city
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "var latitude = ")]/text()'))
            .split("var latitude = ")[1]
            .split(";")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "var longitude = ")]/text()'))
            .split("var longitude = ")[1]
            .split(";")[0]
            .strip()
        )
        phone = "".join(
            tree.xpath('//i[@class="fa fa-mobile"]/following-sibling::p/span/text()')
        ).strip()
        hours_of_operation = (
            " ".join(tree.xpath('//li[@class="hours-information"]/p//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split()).replace(" :", ":").strip()
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
    locator_domain = "https://www.decathlon.co.jp/"
    api_url = "https://www.decathlon.co.jp/pages/store-finder"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
