from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.costuless.com/"
    api_url = "https://www.costuless.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@id="store-selection"]/li/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.costuless.com{slug}/about-us"
        location_name = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = tree.xpath(
            '//h3[text()="Contact Information"]/following-sibling::p[1]/text()'
        )
        ad = list(filter(None, [a.strip() for a in ad]))
        adr = " ".join(ad[:2]).replace("\n", "").replace("\r", "").strip()
        adr = " ".join(adr.split())

        a = parse_address(International_Parser(), adr)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "VG"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = location_name
        phone = (
            "".join(
                tree.xpath(
                    '//strong[contains(text(), "Tel")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .replace("\r", "")
            .strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            for p in ad:
                if "Tel" in p:
                    phone = (
                        str(p)
                        .replace("\n", "")
                        .replace("\r", "")
                        .replace("Tel:", "")
                        .strip()
                    )
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
            )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Hours of Operation")]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .replace("\r", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        r = session.get("https://www.costuless.com/store-locator", headers=headers)
        tree = html.fromstring(r.text)
        try:
            latitude = (
                "".join(
                    "".join(
                        tree.xpath('//script[contains(text(), "var locations")]/text()')
                    ).split(f'{slug.replace("/","")}')[1:]
                )
                .split('"lat":"')[1]
                .split('"')[0]
                .strip()
            )
            longitude = (
                "".join(
                    "".join(
                        tree.xpath('//script[contains(text(), "var locations")]/text()')
                    ).split(f'{slug.replace("/", "")}')[1:]
                )
                .split('"lng":"')[1]
                .split('"')[0]
                .strip()
            )
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
