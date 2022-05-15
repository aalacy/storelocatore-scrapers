import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://fit4lifehealthclubs.com/"
    api_url = "https://fit4lifehealthclubs.com/find-a-gym/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "map_options")]/text()'))
        .split('"places":')[1]
        .split(',"listing"')[0]
    )
    js = json.loads(div)
    for j in js:

        location_name = j.get("title")
        info = j.get("content")
        b = html.fromstring(info)
        page_url = "".join(b.xpath("//a/@href"))
        content = "<MISSING>"
        if page_url == "https://fit4lifehealthclubs.com/fayetteville-2/":
            page_url = api_url
            content = (
                "".join(b.xpath("//text()[1]"))
                .replace("\n", "")
                .replace("\r", "")
                .split("•")[-2]
                .strip()
            )
        ad = j.get("address")
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = j.get("location").get("state")
        postal = j.get("location").get("postal_code")
        country_code = "US"
        city = j.get("location").get("city")
        store_number = j.get("id")
        latitude = j.get("location").get("lat")
        longitude = j.get("location").get("lng")
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        phone = (
            "".join(
                tree.xpath(
                    '//*[./*[contains(text(), "PHONE")]]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath('//*[./*[contains(text(), "PHONE")]]//span/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if phone == "<MISSING>":
            phone = content
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    "//div[.//iframe]/following::h2[1]/following-sibling::p[1]//text()"
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        "//div[.//iframe]/following::h1[1]/following-sibling::p[1]//text()"
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        cms = "".join(tree.xpath('//*[contains(text(), "Opening Soon")]/text()'))
        if cms:
            hours_of_operation = "Coming Soon"
        hours_of_operation = hours_of_operation.replace("/span>", "").strip()

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
