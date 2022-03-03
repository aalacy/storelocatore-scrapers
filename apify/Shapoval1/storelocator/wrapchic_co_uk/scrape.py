import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://wrapchic.co.uk/"
    api_url = "https://wrapchic.co.uk/find-wrapchic/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="section group all_locations"]/div[@class="col span_4_of_12"]'
    )
    for d in div:
        location_name = (
            "".join(d.xpath('.//*[@class="locationtitle"]/text()'))
            .replace("\n", "")
            .strip()
        )
        info1 = (
            " ".join(d.xpath(".//*//text()"))
            .replace("\n", " ")
            .replace(" ", "")
            .replace("-", "")
            .strip()
        )
        ad = (
            " ".join(d.xpath(".//h2/following-sibling::p[1]//text()"))
            .replace("\n", " ")
            .strip()
        )
        if location_name.find("Woking – Peacocks Centre") != -1:
            ad = (
                " ".join(
                    d.xpath('.//p[contains(text(), "@")]/preceding-sibling::p//text()')
                )
                .replace("\n", " ")
                .replace("\r", " ")
                .strip()
            )

        ad = (
            " ".join(ad.split())
            .replace("Wrapchic CanterburyUnit 18-9", "Wrapchic Canterbury Unit 1 8-9")
            .replace("The ParadeCanterbury", "The Parade Canterbury")
            .strip()
        )

        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        if "Dubai" in ad:
            country_code = "Dubai"
        city = a.city or "<MISSING>"
        if city == "<MISSING>" and location_name.find("London") != -1:
            city = "London"
        text = "".join(d.xpath('.//a[text()="View Map"]/@href'))
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
            re.findall(
                r"((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))",
                info1,
            )
            or "<MISSING>"
        )
        phone = "".join(phone).replace("\xa0", "").strip()

        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/p[contains(text(), "–")]/text() | .//p[contains(text(), "to ")]/text()'
                )
            )
            .replace("\n", " ")
            .strip()
            or "<MISSING>"
        )
        session = SgRequests()
        r = session.get("https://wrapchic.co.uk/locations/", headers=headers)
        tree = html.fromstring(r.text)
        page_url = "".join(
            tree.xpath(f'//a[contains(text(), "{location_name}")]/@href')
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
