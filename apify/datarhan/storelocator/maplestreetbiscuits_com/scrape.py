from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.maplestreetbiscuits.com/locations/"
    domain = "maplestreetbiscuits.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//a[@class="brz-a brz-container-link"]/@href')
    for url in all_states:
        url = urljoin(start_url, url)
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_urls = dom.xpath(
            '//div[@id]/a[@data-brz-link-type="external" and span]/@href'
        )
        all_locations = []
        for url in all_urls:
            if url == "https://www.maplestreetbiscuits.com/":
                break
            all_locations.append(url)

        for page_url in all_locations:
            if not page_url:
                continue
            passed = True
            exc = [
                "our-menu-2",
                "about",
                "join-the-team",
                "legal",
                "page_id",
                "careers",
                "immerse-marketing",
            ]
            for e in exc:
                if e in page_url:
                    passed = False
            if not passed:
                continue

            loc_response = session.get(page_url, headers=hdr)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)
            raw_data = loc_dom.xpath(
                '//div[p[span[contains(text(), "WELCOME TO")]]]/p//text()'
            )
            if len(raw_data) == 1:
                raw_data = loc_dom.xpath(
                    '//div[div[div[p[span[contains(text(), "WELCOME TO ")]]]]]/following-sibling::div[1]//text()'
                )
                raw_data = ["-"] + raw_data
            if not raw_data:
                raw_data = loc_dom.xpath(
                    '//h1[span[contains(text(), "WELCOME TO")]]/following-sibling::h1/span/text()'
                )
            raw_data = [e.strip() for e in raw_data if e.strip()]
            location_name = page_url.split("/")[-2].replace("-", " ").capitalize()
            if not raw_data:
                street_address = "<INACCESSIBLE>"
                city = "<INACCESSIBLE>"
                state = "<INACCESSIBLE>"
                zip_code = "<INACCESSIBLE>"
                phone = "<INACCESSIBLE>"
            else:
                if len(raw_data) > 3:
                    raw_address = raw_data[1:3]
                else:
                    raw_address = raw_data[:2]
                if "Suit" in raw_data[2]:
                    raw_address = raw_data[1:4]
                    raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
                street_address = raw_address[0]
                city = raw_address[1].split(", ")[0]
                state = raw_address[1].split(", ")[-1].split()[0]
                zip_code = raw_address[1].split(", ")[-1].split()[-1]
                phone = [e.strip() for e in raw_data if e.split("-")[0].isdigit()]
                if not phone:
                    phone = [e.strip() for e in raw_data if "(" in e]
                phone = phone[0] if phone else ""

            hoo = loc_dom.xpath('//*[contains(text(), "am to ")]/text()')
            if not hoo:
                hoo = loc_dom.xpath('//strong[contains(text(), "AM ")]/text()')
            if not hoo:
                hoo = loc_dom.xpath('//*[contains(text(), "am –")]/text()')
            if not hoo:
                hoo = loc_dom.xpath(
                    '//p[strong[contains(text(), "SUN – SAT")]]//text()'
                )
            hoo = " ".join(hoo).split("My")[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
