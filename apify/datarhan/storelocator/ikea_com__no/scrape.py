from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.ikea.com/no/no/stores/"
    domain = "ikea.com/no"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//strong/a[contains(@href, "/stores/")]/@href')
    for page_url in all_locations:
        if "planning-studio" in page_url:
            continue
        response = session.get(page_url)
        dom = etree.HTML(response.text)
        url = dom.xpath('//a[contains(@href, "varehusinformasjon")]/@href')[0]
        loc_response = session.get(url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = dom.xpath("//h1/text()")[0]
        raw_adr = loc_dom.xpath(
            '//h3[strong[contains(text(), "Varehuset")]]/following-sibling::p[1]/text()'
        )
        if not raw_adr:
            raw_adr = loc_dom.xpath('//p[strong[contains(text(), "Adresse")]]/text()')
        if raw_adr:
            raw_adr = [e.strip() for e in raw_adr if "IKEA" not in e]
            raw_adr = [e.strip() for e in raw_adr if "Telefon" not in e]
            raw_adr = " ".join(raw_adr).split("Bring utleveringssted")[0].strip()
        else:
            raw_adr = " ".join(
                loc_dom.xpath(
                    '//*[strong[contains(text(), "Adresse")]]/following-sibling::p[1]/text()'
                )
            )
        addr = parse_address_intl(raw_adr)
        zip_code = addr.postcode
        city = addr.city
        if not city:
            city = raw_adr.split(zip_code)[-1].strip()
        street_address = raw_adr.split(zip_code)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        phone = loc_dom.xpath('//p[strong[contains(text(), "Telefon")]]/text()')
        if not phone:
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        if not phone:
            phone = loc_dom.xpath('//a[contains(@href, "tlf")]/text()')
        phone = phone[0].split("oss på")[-1].strip() if phone else ""
        if not phone:
            phone = (
                loc_dom.xpath('//p[strong[contains(text(), "Adresse")]]/text()')[-1]
                .split(":")[-1]
                .strip()
            )
        if city in phone:
            phone = ""
        if not phone:
            phone = loc_dom.xpath(
                '//h3[contains(text(), "Kontakt oss")]/following-sibling::p[1]/text()'
            )
            if phone:
                phone = phone[0].split("oss på")[-1].strip()
            else:
                phone = loc_dom.xpath(
                    '//p[strong[contains(text(), "Adresse og telefon:")]]/following-sibling::p[1]/text()'
                )
                phone = phone[0] if phone else ""
                if not phone:
                    phone = loc_dom.xpath(
                        '//p[a[@href="https://freetrailer.com/no/"]]/text()'
                    )
                    phone = phone[-1].split("telefon")[-1].strip()[:-1] if phone else ""

        geo = loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
        if "/@" in geo:
            geo = geo.split("/@")[-1].split(",")[:2]
        else:
            geo = (
                loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
                .split("ll=")[-1]
                .split("&")[0]
                .split(",")
            )
        hoo = dom.xpath('//div[p[strong[contains(text(), "Åpningstider")]]]/p/text()')
        if hoo and "Sisters" in hoo[0]:
            hoo = ""
        if not hoo:
            hoo = dom.xpath(
                '//h2[strong[contains(text(), "Åpningstider")]]/following-sibling::p[1]/text()'
            )
        if not hoo:
            hoo = dom.xpath(
                '//h2[strong[contains(text(), "Åpningstider")]]/following-sibling::p[2]/text()'
            )
        if not hoo:
            hoo = dom.xpath('//h3[strong[contains(text(), "Åpningstider")]]/text()')
        if not hoo:
            hoo = dom.xpath('//h2[strong[contains(text(), "Åpent:")]]/strong[2]/text()')
        if not hoo:
            hoo = dom.xpath(
                '//h2[contains(text(), "Åpningstider")]/following-sibling::p/text()'
            )
        if not hoo:
            hoo = dom.xpath(
                '//p[strong[contains(text(), "Varehuset")]]/following-sibling::p[1]//text()'
            )
        hoo = " ".join(hoo).split("Rest")[0].strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="NO",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
            raw_address=raw_adr,
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
