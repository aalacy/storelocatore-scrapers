from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.taco-bell.ro"
    api_url = "https://www.taco-bell.ro/restaurante/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="restaurant-card__info"]')
    for d in div:

        page_url = "".join(d.xpath('.//a[@class="restaurant-card__link"]/@href'))
        location_name = "".join(
            d.xpath('.//h2[@class="restaurant-card__title"]/text()')
        )
        ad = (
            " ".join(
                d.xpath(
                    './/b[contains(text(), "Adresă")]/following-sibling::p[1]/text()'
                )
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
        country_code = "Romania"
        city = a.city or "<MISSING>"
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        hours_of_operation = (
            "".join(
                d.xpath(
                    './/b[contains(text(), "Program")]/following-sibling::p[1]/text()'
                )
            )
            .replace("\n", "")
            .replace("Take-away:", "")
            .strip()
        )
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        text = "".join(
            tree.xpath('//button[contains(@onclick, "window.open")]/@onclick')
        )
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
