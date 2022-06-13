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

    session = SgRequests()
    locator_domain = "https://churchschicken.ca/"
    api_urls = [
        "https://alberta.churchstexaschicken.com/Location",
        "https://ontario.churchstexaschicken.com/Location",
        "https://lowermainland.churchstexaschicken.com/Location",
    ]
    for api_url in api_urls:

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@id="M_2"]')
        for d in div:

            slug = "".join(d.xpath('.//p[@class="h4"]/a/@href'))
            page_url = f"{api_url.split('/Location')[0].strip()}{slug}"
            location_name = (
                "".join(d.xpath('.//p[@class="h4"]/a/text()')).replace("\n", "").strip()
            )
            ad = (
                "".join(d.xpath('.//p[@class="h4"]/following-sibling::p[1]/text()'))
                .replace("\n", "")
                .strip()
            )

            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = a.state or "<MISSING>"
            if state == "<MISSING>" and page_url.find("ontario") != -1:
                state = "ON"
            postal = a.postcode or "<MISSING>"
            country_code = "CA"
            city = a.city or "<MISSING>"
            phone = (
                "".join(
                    d.xpath(
                        './/span[contains(text(), "Mobile Number:")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/span[contains(text(), "Opening Daily:")]/following-sibling::text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            with SgFirefox() as driver:

                driver.get(page_url)
                driver.implicitly_wait(30)
                driver.maximize_window()
                driver.switch_to.frame(0)
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//div[@class="bottom-actions"]')
                        )
                    )
                except:
                    driver.switch_to.default_content()
                try:
                    ll = driver.find_element_by_xpath(
                        '//div[@class="google-maps-link"]/a'
                    ).get_attribute("href")
                except:
                    ll = "<MISSING>"
                ll = "".join(ll)
                driver.switch_to.default_content()
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
