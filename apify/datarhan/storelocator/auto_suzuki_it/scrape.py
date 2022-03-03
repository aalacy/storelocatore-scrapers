import re
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://auto.suzuki.it/dealer/index-store-locator.aspx"
    domain = "auto.suzuki.it"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "Coordinate")]/text()')[0]
        .split("ClientMap,")[-1]
        .split(", null, null, $get")[0]
    )
    data = json.loads(data)
    locs_html = etree.HTML(data["Coordinate"])

    all_locations = locs_html.xpath('//p[span[@class="nome_conc"]]')
    for loc in all_locations:
        loc_type = loc.xpath(
            './/following-sibling::div[@class="servizi"]//img[contains(@src, "ico-vendita.gif")]'
        )
        if not loc_type:
            continue
        url = loc.xpath(".//a/@href")[0]
        if "concessionari-suzuk" in url:
            response = session.get(url + "/sedi/")
            dom = etree.HTML(response.text)
            all_poi = dom.xpath('//a[@class="card-dealership__link"]/@href')
            for page_url in all_poi:
                loc_response = session.get(page_url)
                loc_dom = etree.HTML(loc_response.text)

                location_name = loc_dom.xpath("//h1/text()")[0].strip()
                street_address = loc_dom.xpath(
                    '//span[@itemprop="streetAddress"]/text()'
                )[0]
                city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
                city = city[0] if city else ""
                zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
                zip_code = zip_code[0].strip() if zip_code else ""
                phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
                phone = phone[0] if phone else ""
                latitude = loc_dom.xpath("//@data-lat")
                latitude = latitude[0] if latitude else ""
                longitude = loc_dom.xpath("//@data-lng")
                longitude = longitude[0] if longitude else ""
                hoo = loc_dom.xpath(
                    '//section[h4[contains(text(), "Showroom")]]//p//text()'
                )
                if not hoo:
                    hoo = loc_dom.xpath('//span[@itemprop="openingHours"]//text()')
                hoo = (
                    ", ".join([e.strip() for e in hoo if e.strip()])
                    .split("Chiusura")[0]
                    .strip()
                )
                hoo = (
                    " ".join(hoo.split())
                    .split(", Chiuso:")[0]
                    .split("Chiusura:")[0]
                    .split(", Chiuso per")[0]
                    .split(", CHIUSURA")[0]
                    .split(", Festività")[0]
                    .split("Assistenza")[0]
                    .split("Chiuso:")[0]
                    .split("Domenica: Chiuso")[0]
                    + " Domenica: Chiuso"
                )

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state="",
                    zip_postal=zip_code,
                    country_code="IT",
                    store_number="",
                    phone=phone,
                    location_type="",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hoo,
                )

                yield item
        else:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            location_name = loc_dom.xpath(
                '//span[@id="ctl00_ContentPlaceHolder1_lbDealerName"]/text()'
            )[0]
            street_address = loc_dom.xpath(
                '//span[@id="ctl00_ContentPlaceHolder1_lbAddress"]/text()'
            )[0]
            zip_code = loc_dom.xpath(
                '//span[@id="ctl00_ContentPlaceHolder1_lbZip"]/text()'
            )[0]
            city = loc_dom.xpath(
                '//span[@id="ctl00_ContentPlaceHolder1_lbTown"]/text()'
            )[0]
            state = loc_dom.xpath(
                '//span[@id="ctl00_ContentPlaceHolder1_lbProv"]/text()'
            )[0]
            phone = loc_dom.xpath(
                '//span[@id="ctl00_ContentPlaceHolder1_lbTel"]/text()'
            )
            phone = phone[0].split(":")[-1].strip() if phone else ""

            hoo_url = loc_dom.xpath('//a[@class="btn-orari"]/@href')[0]
            hoo_response = session.get(urljoin(page_url, hoo_url))
            hoo_dom = etree.HTML(hoo_response.text)
            hoo = hoo_dom.xpath("//text()")
            if hoo and "Showroom" in " ".join(hoo):
                hoo = (
                    " ".join([e.strip() for e in hoo if e.strip()])
                    .split("Showroom ")[-1]
                    .strip()
                )
            else:
                hoo = ""
            if hoo:
                hoo = hoo = (
                    " ".join(hoo.split())
                    .split(", Chiuso:")[0]
                    .split("Chiusura:")[0]
                    .split(", Chiuso per")[0]
                    .split(", CHIUSURA")[0]
                    .split(", Festività")[0]
                    .split("Assistenza")[0]
                    .split("Chiuso:")[0]
                    .split("Domenica: Chiuso")[0]
                    + " Domenica: Chiuso"
                )

            latitude = re.findall(r'lat":(.+?),', loc_response.text)[0]
            longitude = re.findall(r'lng":(.+?)\}', loc_response.text)[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="IT",
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
