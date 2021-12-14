import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_urls = {
        "Singapore": "https://www.lexus.com.sg/en/contact-us/find-a-dealer.html",
        "Brunei": "https://www.lexus.com.bn/en/contact-us/find-a-dealer.html",
        "Indonesia": "https://www.lexus.co.id/en/contact-us/find-a-dealer.html",
        "Malaysia": "https://www.lexus.com.my/en/contact-us/find-a-dealer.html",
        "Philippines": "https://www.lexus.com.ph/en/contact-us/find-a-dealer.html",
        "Vietnam": "https://www.lexus.com.vn/vn/contact-us/find-a-dealer.html",
        "Thailand": "https://www.lexus.co.th/en/contact-us/find-a-dealer.html",
        "Bolivia": "https://www.lexus.com.bo/es/contact-us/find-a-dealer.html",
        "Brazil": "https://www.lexus.com.br/pt/contact-us/find-a-dealer.html",
        "Chile": "https://www.lexus.cl/es/contact-us/find-a-dealer.html",
        "Costa Rica": "https://www.lexuscostarica.com/es/contact-us/find-a-dealer.html",
        "Guatemala": "https://www.lexus.gt/es/contact-us/find-a-dealer.html",
        "New Zeland": "https://www.lexus.co.nz/en/contact-us/find-a-dealer.html",
        "Peru": "https://www.lexusperu.com.pe/es/contact-us/find-a-dealer.html",
        "Paraguay": "https://www.lexus.com.py/es/contact-us/find-a-dealer.html",
        "Panama": "https://www.lexusrp.com/es/contact-us/find-a-dealer.html",
    }
    domain = "lexus.com.sg"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for country_code, start_url in start_urls.items():
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)
        data = (
            dom.xpath('//script[contains(text(), "dealers")]/text()')[0]
            .strip()[:-1]
            .split('locations":')[-1][:-3]
        )
        all_locations = json.loads(data)
        for poi in all_locations:
            if not poi["addressLines"]:
                continue
            raw_address = poi["addressLines"][0]["line"]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            page_url = (
                poi["url"] if poi.get("url") and "http" in poi["url"] else start_url
            )
            geo = poi["addressUrl"].split("/@")[-1].split(",")[:2]
            if "https" in poi["addressUrl"] and "@" in poi["addressUrl"]:
                if len(geo[0]) > 12:
                    geo = poi["addressUrl"].split("=")[-1].split(",")
            if len(geo) == 1:
                geo = ["", ""]
            hoo = []
            for e in poi["openingHrsFulls"]:
                hoo.append(f'{e["day"]}: {e["time"]}')
            hoo = (
                " ".join(hoo)
                .replace("<br> ", "")
                .split("<b>Easter")[0]
                .split("Customer")[0]
                .split("Dịch vụ:")[0]
                .strip()
            )
            phone = poi["phoneNos"]
            phone = phone[0]["tel"] if phone else ""
            zip_code = addr.postcode
            if zip_code:
                zip_code = zip_code.replace("CEP", "").strip()

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["header"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_code,
                country_code=poi["country"],
                store_number="",
                phone=phone,
                location_type="",
                latitude=geo[0],
                longitude=geo[1],
                hours_of_operation=hoo,
                raw_address=raw_address,
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
