from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://coolgreens.com/"
    api_url = "https://coolgreens.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Explore"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        location_name = (
            "".join(d.xpath(".//preceding::p[2]/text()[1]")).replace("\n", "").strip()
            or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = (
                "".join(d.xpath(".//preceding::p[1]/text()[1]"))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            " ".join(
                tree.xpath(
                    '//div[@class="et_pb_section et_pb_section_1 et_pb_with_background et_section_specialty"]//div[@class="et_pb_module et_pb_text et_pb_text_1  et_pb_text_align_left et_pb_bg_layout_light"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        text = (
            "".join(
                tree.xpath('//script[contains(text(), "var et_animation_data")]/text()')
            )
            .replace("\n", "")
            .split("var et_link_options_data")[1]
            .strip()
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
        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="et_pb_section et_pb_section_1 et_pb_with_background et_section_specialty"]//div[@class="et_pb_module et_pb_text et_pb_text_2  et_pb_text_align_left et_pb_bg_layout_light"]//p[last()]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(
                    tree.xpath(
                        '//div[@class="et_pb_section et_pb_section_1 et_pb_with_background et_section_specialty"]//div[@class="et_pb_module et_pb_text et_pb_text_2  et_pb_text_align_left et_pb_bg_layout_light"]//p[last() - 1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./span[contains(text(), "pm")]]//text() | //p[./span[contains(text(), "Mon.")]]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        location_name = "".join(tree.xpath('//meta[@property="og:title"]/@content'))

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
