from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://honda-mideast.com/"
    page_urls = [
        "https://www.honda-mideast.com/en-bh/dealer-contacts/contacts-bahrain",
        "https://www.honda-mideast.com/en-sa/dealer-contacts/contacts-ksa?id=9054A2B8AE7748F9A92B1D3C87817072",
        "https://www.honda-mideast.com/en-bj/dealer-contacts/contacts-benin",
        "https://www.honda-mideast.com/en-gh/dealer-contacts/contacts-ghana",
        "https://www.honda-mideast.com/en-kw/dealer-contacts/contacts-kuwait",
        "https://www.honda-mideast.com/en-lb/dealer-contacts/contacts-lebanon",
        "https://www.honda-mideast.com/en-om/dealer-contacts/contacts-oman",
        "https://www.honda-mideast.com/en-jo/dealer-contacts/contacts-jordan",
        "https://www.honda-mideast.com/en-qa/dealer-contacts/contacts-qatar",
        "https://www.honda-mideast.com/fr-tn/dealer-contacts/contacts-tunisia",
    ]
    for page_url in page_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath(
            '//h2[text()="SHOWROOMS"]/following-sibling::div | //h2[text()="SHOWROOM"]/following-sibling::div'
        )
        for d in div:

            location_name = "".join(d.xpath(".//h4/text()")) or "<MISSING>"
            location_type = (
                "".join(
                    d.xpath(
                        './/span[contains(text(), "Category")]/following-sibling::text()'
                    )
                ).strip()
                or "<MISSING>"
            )
            ad = (
                "".join(
                    d.xpath(
                        './/span[contains(text(), "Address")]/following-sibling::text()'
                    )
                ).strip()
                or "<MISSING>"
            )
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            if street_address == "<Missing>":
                street_address = ad
            state = (
                "".join(
                    d.xpath(
                        './/span[contains(text(), "Region")]/following-sibling::text()'
                    )
                ).strip()
                or "<MISSING>"
            )
            postal = (
                "".join(
                    d.xpath(
                        './/span[contains(text(), "Postal Code")]/following-sibling::text()'
                    )
                ).strip()
                or "<MISSING>"
            )
            country_code = (
                page_url.split("/dealer")[0].split("-")[-1].upper().strip()
                or "<MISSING>"
            )
            city = (
                "".join(
                    d.xpath(
                        './/span[contains(text(), "City")]/following-sibling::text()'
                    )
                ).strip()
                or "<MISSING>"
            )
            if city.find("Cotonou") != -1:
                city = "Cotonou"
            text = "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
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
                    d.xpath(
                        './/p[@class="desktop_contact"]/span[contains(text(), "Phone")]/following-sibling::a[1]/@href'
                    )
                )
                .replace("tel:", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                "".join(
                    d.xpath(
                        './/span[contains(text(), "Timings")]/following-sibling::text()'
                    )
                ).strip()
                or "<MISSING>"
            )
            if street_address == "<MISSING>":
                location_type = (
                    "".join(
                        d.xpath(
                            './/span[contains(text(), "Catégorie")]/following-sibling::text()'
                        )
                    ).strip()
                    or "<MISSING>"
                )
                ad = (
                    "".join(
                        d.xpath(
                            './/span[contains(text(), "Adresse")]/following-sibling::text()'
                        )
                    ).strip()
                    or "<MISSING>"
                )
                a = parse_address(International_Parser(), ad)
                street_address = (
                    f"{a.street_address_1} {a.street_address_2}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
                if street_address == "<Missing>":
                    street_address = ad
                state = (
                    "".join(
                        d.xpath(
                            './/span[contains(text(), "Région")]/following-sibling::text()'
                        )
                    ).strip()
                    or "<MISSING>"
                )
                postal = (
                    "".join(
                        d.xpath(
                            './/span[contains(text(), "Code Postal")]/following-sibling::text()'
                        )
                    ).strip()
                    or "<MISSING>"
                )
                city = (
                    "".join(
                        d.xpath(
                            './/span[contains(text(), "ville")]/following-sibling::text()'
                        )
                    ).strip()
                    or "<MISSING>"
                )
                phone = (
                    "".join(
                        d.xpath(
                            './/p[@class="desktop_contact"]/span[contains(text(), "Téléphone")]/following-sibling::a[1]/@href'
                        )
                    )
                    .replace("tel:", "")
                    .strip()
                    or "<MISSING>"
                )
                hours_of_operation = (
                    "".join(
                        d.xpath(
                            './/span[contains(text(), "Calendrier")]/following-sibling::text()'
                        )
                    ).strip()
                    or "<MISSING>"
                )
                if phone.find("|") != -1:
                    phone = phone.split("|")[0].strip()

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
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
