from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sodimac.com.mx/"
    api_url = "https://www.sodimac.com.mx/sodimac-mx/content/a40055/Tiendas"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@id="folder_5"]//li//a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.sodimac.com.mx{slug}"
        location_name = "".join(d.xpath(".//text()"))
        if page_url.find("Corporativo") != -1:
            continue
        with SgFirefox() as driver:

            driver.get(page_url)
            iframe = driver.find_element_by_xpath(
                '//h3[contains(text(), "Localización")]/following-sibling::iframe[1]'
            )
            driver.switch_to.frame(iframe)
            try:
                WebDriverWait(driver, 10).until(
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
            ad = (
                "".join(ad)
                .replace(", N.L.", "")
                .replace(", Mor.", "")
                .replace(", Méx.", "")
                .replace(", S.L.P.", "")
                .replace(", Ver.", "")
                .replace(", Gto.", "")
                .strip()
            )
            driver.switch_to.default_content()
            location_name = "".join(location_name)
            street_address = "<MISSING>"
            country_code = "MX"
            city = page_url.split("Tienda-")[1].replace("-", " ").strip()
            postal = "<MISSING>"
            if ad != "<MISSING>":
                postal = ad.split(",")[-1].split()[0].strip()
                street_address = ad.split(f", {postal}")[0].strip()
            try:
                latitude = ll.split("ll=")[1].split(",")[0].strip()
                longitude = ll.split("ll=")[1].split(",")[1].split("&")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = driver.find_element_by_xpath(
                '//span[text()="Venta Telefónica"]/following-sibling::span'
            ).text
            hours_of_operation = driver.find_element_by_xpath(
                '//span[./strong[text()="Horarios de Tienda:"]]/following-sibling::span[1]'
            ).text

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
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
