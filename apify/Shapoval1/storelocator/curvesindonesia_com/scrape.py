from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from sgselenium.sgselenium import SgFirefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fetch_data(sgw: SgWriter):

    locator_domain = "https://curvesindonesia.com/"
    for i in range(1, 100):
        api_url = f"https://curvesindonesia.com/lokasi/page/{i}/?lang=en"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="col-md-4 col-sm-6 col-xs-12"]')
        for d in div:

            page_url = "".join(d.xpath("./a[1]/@href"))
            location_name = (
                "".join(d.xpath('.//div[@class="title my-elipsis"]/text()[1]'))
                .replace("\n", "")
                .strip()
            ) or "<MISSING>"
            state = (
                "".join(d.xpath('.//div[@class="title my-elipsis"]/text()[2]'))
                .replace("\n", "")
                .strip()
            )
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            if location_name == "<MISSING>":
                location_name = (
                    "".join(tree.xpath('//h3[@class="title-lokasi"]//text()'))
                    .replace("\n", "")
                    .strip()
                )

            ad = (
                "".join(tree.xpath('//div[@class="alamat-lokasi"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            postal = a.postcode or "<MISSING>"
            country_code = "ID"
            city = a.city or "<MISSING>"
            latitude = "".join(tree.xpath("//div/@data-lat")) or "<MISSING>"
            longitude = "".join(tree.xpath("//div/@data-lng")) or "<MISSING>"
            map_link = "".join(tree.xpath("//iframe/@src"))
            if latitude == "<MISSING>":
                try:
                    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
                except:
                    latitude, longitude = "<MISSING>", "<MISSING>"
            phone = (
                "".join(tree.xpath('//div[@class="kontak-lokasi"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if phone.find("(") != -1:
                phone = phone.split("(")[0].replace("-", "").strip()
            hours_of_operation = (
                " ".join(tree.xpath('//div[@class="email-lokasi"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if hours_of_operation.find("Jadwal:") != -1:
                hours_of_operation = hours_of_operation.split("Jadwal:")[1].strip()

            if street_address == "<MISSING>" or street_address == "<Missing>":
                with SgFirefox() as driver:
                    driver.get(page_url)
                    driver.implicitly_wait(10)
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
                        ad = driver.find_element_by_xpath(
                            '//div[@class="address"]'
                        ).text
                    except:
                        ad = "<MISSING>"
                    ad = "".join(ad)

                    driver.switch_to.default_content()
                    a = parse_address(International_Parser(), ad)

                    phone = "<MISSING>"
                    street_address = (
                        f"{a.street_address_1} {a.street_address_2}".replace(
                            "None", ""
                        ).strip()
                    )
                    state = a.state or "<MISSING>"
                    postal = a.postcode or "<MISSING>"
                    country_code = "ID"
                    city = a.city or "<MISSING>"
                    location_name = driver.find_element_by_xpath(
                        "//h3[@class='title-lokasi']"
                    ).text
                    hours_of_operation = "<MISSING>"

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

        if len(div) != 12:
            break


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
