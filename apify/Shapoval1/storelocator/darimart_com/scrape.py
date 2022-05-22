from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.firefox import GeckoDriverManager
from sgselenium import SgFirefox
from sglogging import SgLogSetup

STORE_LOCATOR = "https://www.darimart.com/locations/"
logger = SgLogSetup().get_logger("darimart_com")


def fetch_data(sgw: SgWriter):
    with SgFirefox(
        executable_path=GeckoDriverManager().install(), block_third_parties=True
    ) as driver:
        driver.get(STORE_LOCATOR)
        logger.info(f"Pulling the content from {STORE_LOCATOR}")
        driver.implicitly_wait(30)
        pgsrcf = driver.page_source
        tree = html.fromstring(pgsrcf)
        div = "".join(
            tree.xpath('//script[contains(text(), "mapboxgl.accessToken")]/text()')
        ).split(".setHTML(")

        for d in div:
            latitude = d.split(".setLngLat([")[-1].split(",")[1].split("]")[0].strip()
            longitude = d.split(".setLngLat([")[-1].split(",")[0].strip()

            ad = d.split(");")[0].strip()
            if ad.find("<p>") == -1:
                continue
            a = html.fromstring(ad)
            csz = (
                " ".join(a.xpath("//p/strong/following-sibling::text()[1]"))
                .replace("\r\n", "")
                .replace("35831 Hwy 58", "")
                .strip()
            )
            if csz == "Mon-Th 5:30am-10pm":
                csz = "<MISSING>"
            page_url = "https://www.darimart.com/locations/"
            street_address = "".join(a.xpath("//*/strong[1]/text()"))
            state = "<MISSING>"
            postal = "<MISSING>"
            country_code = "US"
            city = "<MISSING>"
            phone = "".join(a.xpath('//a[contains(@href, "tel")]/text()'))
            if csz != "<MISSING>":
                state = csz.split(",")[1].split()[0].strip()
                postal = csz.split(",")[1].split()[-1].strip()
                city = csz.split(",")[0].strip()
            try:
                store_number = street_address.split("#")[1].strip()
            except:
                store_number = "<MISSING>"
            hours_of_operation = (
                " ".join(
                    a.xpath(
                        '//*[contains(text(), "pm")]/text() | //*[contains(text(), "am-")]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )

            row = SgRecord(
                locator_domain="darimart.com",
                page_url=page_url,
                location_name=SgRecord.MISSING,
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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
