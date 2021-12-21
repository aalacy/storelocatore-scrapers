import re
from lxml import etree
from urllib.parse import urljoin

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://www.telepizza.pl/lokale"
    domain = "telepizza.pl"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//div[@id="local_list_body"]//a/@href')
        for url in list(set(all_locations)):
            if url == "#":
                continue
            page_url = urljoin(start_url, url)
            driver.get(page_url)
            loc_dom = etree.HTML(driver.page_source)
            location_name = loc_dom.xpath("//section/h2/text()")[0].split(", ")[0]
            if "Lokale" in location_name:
                continue
            city = " ".join(location_name.split()[1:])
            street_address = loc_dom.xpath("//section/h2/text()")[0].split(", ")[-1]
            phone = loc_dom.xpath('//span[contains(@class, "phone")]/text()')[0]
            latitude = re.findall(r"lat: (.+?),", driver.page_source)[0]
            longitude = re.findall(r"lng: (.+?) \}", driver.page_source)[0]
            hoo = loc_dom.xpath(
                '//span[contains(text(), "Godziny otwarcia")]/following-sibling::span/text()'
            )
            hoo = (
                ", ".join([e.strip() for e in hoo])
                .split(", Dostawa")[0]
                .split(", Uwaga")[0]
                .split(", W dniach")[0]
                .split(", UWAGA")[0]
                .split(", Organizujemy")[0]
                .split(", ,")[0]
                .split(", poniedziałek - czwartek:")[0]
                .strip()
            )
            if "00, niedziela - czwartek" in hoo:
                hoo = hoo.split("00, niedziela - czwartek")[0] + "00"
            if ", niedziela: nieczynne" in hoo:
                hoo = hoo.split(", niedziela: nieczynne")[0] + ", niedziela: nieczynne"
            if hoo.endswith(","):
                hoo = hoo[:-1]
            hoo = hoo.replace("LOKAL:, ", "")

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state="",
                zip_postal="",
                country_code="PL",
                store_number="",
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
