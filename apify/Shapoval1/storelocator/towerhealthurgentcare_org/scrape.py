from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://towerhealth.org"

    for i in range(6):

        api_url = f"https://towerhealth.org/locations?f%5B0%5D=location_type%3AUrgent%20Care&page={i}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath(
            '//div[contains(@class, "teaser location js-section-animation")]//h2[@class="teaser__name"]/a'
        )

        for d in div:
            slug = "".join(d.xpath(".//@href"))
            page_url = f"{locator_domain}{slug}"
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = "".join(
                tree.xpath('//h1[@class="location-hero__title"]/text()')
            )
            location_type = "Urgent care"
            ad = tree.xpath(
                '//span[contains(text(), "Address")]/following-sibling::span/text()'
            )
            street_address = "".join(ad[0])
            if len(ad) > 2:
                street_address = street_address + " " + "".join(ad[1])
            adr = "".join(ad[-1])
            phone = "".join(
                tree.xpath(
                    '//span[contains(text(), "Main")]/following-sibling::*/text()'
                )
            )
            state = adr.split(",")[1].split()[0].strip()
            postal = adr.split(",")[1].split()[1].strip()
            country_code = "US"
            city = adr.split(",")[0].strip()
            hours_of_operation = (
                " ".join(tree.xpath('//ul[@class="hours-block__days"]/li//text()'))
                .replace("\n", "")
                .replace("   ", " ")
                .strip()
                or "<MISSING>"
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
                location_type=location_type,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hours_of_operation,
                raw_address=" ".join(ad),
            )
            sgw.write_row(row)
        if len(div) < 10:
            return


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
