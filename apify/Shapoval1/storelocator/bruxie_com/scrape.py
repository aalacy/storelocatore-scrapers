from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://bruxie.com/"
    api_url = "https://bruxie.com/"
    with SgFirefox() as driver:
        driver.get(api_url)
        a = driver.page_source
        tree = html.fromstring(a)
        div = tree.xpath(
            '//h2[text()="BRUXIE LOCATIONS"]/following-sibling::div/p[./a]'
        )
        for d in div:
            page_url = "https://bruxie.com/"
            location_name = (
                "".join(d.xpath("./text()[1]")).replace("\n", "").strip() or "<MISSING>"
            )
            ad = " ".join(d.xpath(".//a//text()")).replace("\n", "").strip()
            ad = " ".join(ad.split())
            a = parse_address(USA_Best_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = a.city or "<MISSING>"
            if city.find("Promenade") != -1:
                street_address = street_address + " Promenade"
                city = city.replace("Promenade", "").strip()
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
            info = d.xpath(".//text()")
            info = list(filter(None, [a.strip() for a in info]))
            phone = "".join(info[-1]).strip()
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        f'.//following::p[contains(text(), "{location_name}")]/text()[position() > 1]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split()).replace("**NOW OPEN**", "").strip()
                or "<MISSING>"
            )
            location_type = "<MISSING>"
            if hours_of_operation.find("**COMING SOON**") != -1:
                hours_of_operation = hours_of_operation.replace(
                    "**COMING SOON**", ""
                ).strip()
                location_type = "Coming Soon"

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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
