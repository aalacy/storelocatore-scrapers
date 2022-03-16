import json
import time
from lxml import html
from sgselenium import SgSelenium
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://c-lovers.com"

    api_url = "https://c-lovers.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="more-link"]/a')
    for b in block:

        page_url = "".join(b.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath('//div[@class="maincontent clearfix location"]//h1//text()')
        )
        jsblock = (
            "["
            + "".join(tree.xpath('//script[contains(text(), "telephone")]/text()'))
            + "]"
        )
        hoosoo = "".join(tree.xpath('//span[@class="store-opening-soon"]/text()'))
        js = json.loads(jsblock)
        for j in js:

            location_type = j.get("@type")
            street_address = j.get("address").get("streetAddress")
            country_code = "CA"
            phone = j.get("telephone") or "<MISSING>"
            state = j.get("address").get("addressRegion")
            city = j.get("address").get("addressLocality")
            try:
                hours_of_operation = (
                    " ".join(j.get("openingHours")).replace("[", "").replace("]", "")
                )
            except:
                hours_of_operation = "<MISSING>"
            if hoosoo:
                hours_of_operation = "Temporarily Closed"

            try:
                driver = SgSelenium().firefox()

                driver.get(page_url)
                iframe = driver.find_element_by_xpath("//div[@id='map']/iframe")
                driver.switch_to.frame(iframe)
                time.sleep(5)

                s = driver.find_element_by_xpath(
                    "//div[@class='place-desc-large']/div[@class='address']"
                ).text

                time.sleep(5)
                driver.switch_to.default_content()
                postal = " ".join("".join(s).split(",")[-2].split()[1:])
            except:
                postal = "<MISSING>"
            if str(postal).isdigit():
                postal = "<MISSING>"

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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
