from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://divinesauto.com/"
    api_url = "https://divinesauto.com/page-sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath(
        '//url/loc[contains(text(), "/convenience-stores/")] | //url/loc[contains(text(), "/auto-repair-shops/")]'
    )
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        if page_url.count("/") != 5:
            continue
        if page_url == "https://divinesauto.com/convenience-stores/palouse/":
            page_url = "https://divinesauto.com/convenience-stores/"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1//text()"))
        ad = (
            " ".join(
                tree.xpath(
                    '//h3[./strong[text()="Address"]]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())

        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
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
                    '//h3[./strong[text()="Telephone"]]/following-sibling::p[1]//*/@href'
                )
            )
            .replace("\n", "")
            .replace("tel:", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[./strong[contains(text(), "Convenience Store Hours")]]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h3[./strong[contains(text(), "Hours")]]/following-sibling::p[1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if page_url == "https://divinesauto.com/convenience-stores/":
            location_name = (
                "".join(
                    tree.xpath(
                        '//p[@class="has-text-align-center convenience-store-box"]/text()[last()]'
                    )
                )
                .split("–")[0]
                .strip()
            )
            street_address = (
                "".join(
                    tree.xpath(
                        '//p[@class="has-text-align-center convenience-store-box"]/text()[last()]'
                    )
                )
                .split("–")[1]
                .strip()
            )
        if (
            street_address == "203 W. 3Rd Ave"
            or street_address == "3725 S Grand Blvd"
            or not street_address
            or street_address == "<MISSING>"
        ):
            continue

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
