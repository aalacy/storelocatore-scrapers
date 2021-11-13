import json
import time
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from sgselenium.sgselenium import SgFirefox


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        days = h.get("dayOfWeek")
        if type(days) == list:
            days = " ".join(days)
        opens = h.get("opens")
        closes = h.get("closes")
        line = f"{days} {opens} - {closes}"
        tmp.append(line)

    return ";".join(tmp)


def fetch_data(sgw: SgWriter):
    locator_domain = "https://houseofair.com/"
    api_url = "https://houseofair.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h3/a")
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("https://www.houseofair.pl") != -1:
            page_url = "http://www.houseofair.pl/kontakt"

        location_name = "".join(d.xpath(".//text()")).strip()
        street_address = "".join(d.xpath(".//following::p[1]/text()[1]")).strip()
        ad = "".join(d.xpath(".//following::p[1]/text()[2]")).replace("\n", "").strip()

        a = parse_address(International_Parser(), ad)
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = a.country or "USA"
        city = a.city or "<MISSING>"
        with SgFirefox() as driver:
            time.sleep(5)
            driver.get(page_url)
            time.sleep(5)
            a = driver.page_source
            tree1 = html.fromstring(a)

            js_block = (
                "".join(
                    tree1.xpath('//script[@type="application/ld+json"]/text()')
                ).split("}}]}}")[0]
                + "}}]}}"
            )
            map_link = "".join(tree1.xpath("//iframe/@src"))
            try:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            if latitude == "<MISSING>":
                driver.switch_to.frame(0)
                ll = driver.find_element_by_xpath(
                    '//div[@class="google-maps-link"]/a'
                ).get_attribute("href")
                latitude = ll.split("ll=")[1].split(",")[0].strip()
                longitude = ll.split("ll=")[1].split(",")[1].split("&")[0].strip()
                driver.switch_to.default_content()

            phone_list = tree1.xpath('//a[contains(@href, "tel")][1]//text()')
            phone_list = list(filter(None, [a.strip() for a in phone_list]))
            phone = (
                "".join(phone_list[0]).replace("Phone:", "").replace("\n", "").strip()
            )
            hours_of_operation = (
                " ".join(
                    tree1.xpath(
                        '//h3[contains(text(), "Park Access Hours")]/following-sibling::ul/li//text() | //h2[contains(text(), "Hours of Operation")]/following::ul[1]/li//text() | //div[@class="hours-right"]/p/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if "Phone" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Phone")[0].strip()

            hours_of_operation = " ".join(hours_of_operation.split())
            if hours_of_operation == "<MISSING>" and js_block:
                js = json.loads(js_block)
                hours = js.get("openingHoursSpecification")
                hours_of_operation = get_hours(hours)

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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
