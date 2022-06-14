from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.odwlogistics.com"
    api_url = "https://www.odwlogistics.com/locations-and-reach"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Learn More"]')
    for d in div:

        page_url = "https://www.odwlogistics.com" + "".join(d.xpath(".//@href"))

        with SgFirefox() as driver:

            driver.get(page_url)
            driver.implicitly_wait(3)
            driver.maximize_window()
            driver.switch_to.frame(0)
            try:
                WebDriverWait(driver, 1).until(
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
            except:
                ad = "<MISSING>"
                ll = "<MISSING>"
            ll = "".join(ll)
            ad = "".join(ad)
            driver.switch_to.default_content()

            location_name = driver.find_element_by_xpath(
                '//h2[@class="hero__title title"]'
            ).text
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = a.city or "<MISSING>"
            phone = driver.find_element_by_xpath(
                '//ul[@class="location__specs"]//a[contains(@href, "tel")]'
            ).text
            location_type = driver.find_element_by_xpath(
                '//ul[@class="location__specs"]/li[1]'
            ).text
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
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.LOCATION_TYPE})
        )
    ) as writer:
        fetch_data(writer)
