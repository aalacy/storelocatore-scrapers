from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_urls = {
        "Cameroon": "https://suzuki.cami-cfao.com/fr/concession/suzuki-cameroun-cami",
        "Malawi": "https://suzuki.cfao-malawi.com/en/dealership/suzuki-malawi-cfao-motors",
        "Burkina Faso": "https://suzuki.cfaomotors-burkinafaso.com/fr/concession/suzuki-burkina-faso-cfao-motors",
        "Central African Republic": "https://suzuki.cfaomotors-centrafrique.com/fr/concession/suzuki-centrafrique-cfao-motors",
        "Congo": "https://suzuki.cfaomotors-congo.com/fr/concession/suzuki-congo-cfao-motors",
        "Gabon": "https://suzuki.cfaomotors-gabon.com/fr/concession/suzuki-gabon-cfao-motors",
        "Gambia": "https://suzuki.cfaomotors-gambia.com/en/dealership/suzuki-gambia-cfao-motors",
        "Ghana": "https://suzuki.cfaomotors-ghana.com/en/dealership/suzuki-ghana-cfao-motors",
        "Guinea": "https://suzuki.cfaomotors-guinee.com/fr/concession/suzuki-guinee-cfao-motors",
        "Guinea-Bissau": "https://suzuki.cfaomotors-guineebissau.com/fr/concession/suzuki-guinee-bissau-cfao-motors",
        "Equatrail Guinea": "https://suzuki.cfaomotors-guineeequatoriale.com/fr/concession/suzuki-guinee-equatoriale-cfao-motors",
        "Mali": "https://suzuki.cfaomotors-mali.com/fr/concession/suzuki-mali-cfao-motors",
        "Mauritania": "https://suzuki.cfaomotors-mauritanie.com/fr/concession/suzuki-mauritanie-cmda",
        "Niger": "https://suzuki.cfaomotors-niger.com/fr/concession/suzuki-niger-cfao-motors",
        "Democratic Republic of the Congo": "https://suzuki.cfaomotors-rdc.com/fr/concession/suzuki-rdc-cfao-motors",
        "Senegal": "https://suzuki.cfaomotors-senegal.com/fr/concession/suzuki-senegal-cfao-motors",
        "Sao Tom and Principe": "https://suzuki.cfaomotors-stp.com/en/dealership/suzuki-sao-tome-and-principe-cfao-motors",
        "Chad": "https://suzuki.cfaomotors-tchad.com/fr/concession/suzuki-tchad-cfao-motors",
        "Morocco": "https://www.suzukimaroc.com/fr/concession/suzuki-maroc-cfao-motors",
    }
    domain = "suzuki.cami-cfao.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for country_code, url in start_urls.items():
        response = session.get(url, headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="concessions"]//a/@href')
        for page_url in all_locations:
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath('//div[@class="content-heading"]/h2/text()')
            if not location_name:
                continue
            location_name = location_name[-1]
            raw_address = loc_dom.xpath('//div[@class="location-info"]/div/text()')
            street_address = raw_address[0]
            addr = parse_address_intl(" ".join(raw_address))
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else ""
            types = loc_dom.xpath('//div[@class="concession-services"]//text()')
            types = [e.strip() for e in types if e.strip()]
            location_type = " ".join(types)
            for e in ["New vehicles", "Neuves"]:
                if e not in location_type:
                    continue
            geo = loc_dom.xpath('//script[contains(text(), "map_markers")]/text()')[
                0
            ].split(",")[1:3]
            hoo = loc_dom.xpath('//div[@class="concession-schedules"]/div/text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state="",
                zip_postal="",
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type=location_type,
                latitude=geo[0],
                longitude=geo[1],
                hours_of_operation=hoo,
                raw_address=" ".join(raw_address),
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
