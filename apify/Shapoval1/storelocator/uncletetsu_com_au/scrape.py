from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fetch_data(sgw: SgWriter):

    locator_domain = "https://uncletetsu.com.au"
    page_url = "https://uncletetsu.com.au/locations/"

    with SgFirefox() as driver:
        driver.get(page_url)
        iframes = driver.find_elements_by_xpath("//iframe")
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[@class="address"]')
                    )
                )
            except:
                driver.switch_to.default_content()
            try:
                ad = driver.find_element_by_xpath('//div[@class="address"]').text
                ll = driver.find_element_by_xpath(
                    '//div[@class="google-maps-link"]/a'
                ).get_attribute("href")
                location_name = driver.find_element_by_xpath(
                    '//div[@class="place-name"]'
                ).text
            except:
                ad = "<MISSING>"
                ll = "<MISSING>"
                location_name = "<MISSING>"
            ll = "".join(ll)
            ad = "".join(ad)
            driver.switch_to.default_content()

            street_address = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[1].strip()
            postal = ad.split(",")[1].split()[2].strip()
            country_code = "AU"
            city = ad.split(",")[1].split()[0].strip()
            try:
                latitude = ll.split("ll=")[1].split(",")[0].strip()
                longitude = ll.split("ll=")[1].split(",")[1].split("&")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"

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
                phone=SgRecord.MISSING,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
