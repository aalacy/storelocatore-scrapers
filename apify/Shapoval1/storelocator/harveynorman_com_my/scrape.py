from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.harveynorman.com.my/"
    page_url = "https://www.harveynorman.com.my/customer-services/store-finder.html"
    with SgFirefox() as driver:
        driver.get(page_url)
        a = driver.page_source
        tree = html.fromstring(a)
        div = tree.xpath('//div[./div/h5[text()="Address"]]')
        for d in div:
            info = d.xpath('.//h5[text()="Address"]/following-sibling::p[1]/text()')
            info = list(filter(None, [b.strip() for b in info]))
            ad = " ".join(info[:-1]).replace("\n", "").replace("\r", "").strip()
            ad = " ".join(ad.split())

            location_name = (
                "".join(d.xpath(".//preceding::h4[1]//text()")) or "<MISSING>"
            )
            if location_name == "<MISSING>":
                location_name = (
                    "".join(d.xpath(".//preceding::h3[1]//text()")) or "<MISSING>"
                )
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            if postal == "DARUL":
                postal = "<MISSING>"
            country_code = "MY"
            city = a.city or "<MISSING>"
            map_link = "".join(d.xpath(".//following-sibling::p[1]//iframe/@src"))
            try:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = (
                "".join(
                    d.xpath(
                        './/h5[text()="Address"]/following-sibling::p[1]/text()[last()]'
                    )
                )
                .replace("Phone:", "")
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/h5[text()="Opening Hours"]/following-sibling::p//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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

    locator_domain = "https://www.harveynorman.com.sg/"
    page_url = "https://www.harveynorman.com.sg/store-finder.html"
    with SgFirefox() as driver:
        driver.get(page_url)
        a = driver.page_source
        tree = html.fromstring(a)
        div = tree.xpath('//div[./div/h5[contains(text(), "Address")]]')
        for d in div:
            info = d.xpath(
                './/h5[contains(text(), "Address")]/following-sibling::p[1]/text()'
            )
            info = list(filter(None, [b.strip() for b in info]))
            ad = " ".join(info).replace("\n", "").replace("\r", "").strip()
            ad = " ".join(ad.split())

            location_name = (
                "".join(d.xpath(".//preceding::h4[1]//text()")) or "<MISSING>"
            )
            if location_name == "<MISSING>":
                location_name = (
                    "".join(d.xpath(".//preceding::h3[1]//text()")) or "<MISSING>"
                )
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "SG"
            city = a.city or "<MISSING>"
            map_link = "".join(d.xpath(".//following-sibling::iframe/@src"))
            try:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = (
                "".join(d.xpath('.//p[contains(text(), "Telephone:")]/text()'))
                .replace("Telephone:", "")
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/h5[text()="Opening Hours"]/following-sibling::p//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
