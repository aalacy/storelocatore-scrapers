from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://toyota.mx/distribuidores"
    domain = "toyota.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_estados = dom.xpath('//select[@id="cp_value"]/option/@value')
    for estado in all_estados:
        url = f"https://toyota.mx/api/distribuidores?estado={estado}&tipo=mapa"
        data = session.get(url).json()
        for poi in data["response"]:
            url = f'https://toyota.mx/api/geo?distribuidor={poi["tid"]}&latitud=null&longitud=null&tipo=distribuidor'
            poi_data = session.get(url).json()
            street_address = ""
            city = ""
            zip_code = ""
            if poi_data["description"]:
                raw_address = (
                    etree.HTML(poi_data["description"])
                    .xpath("//text()")[0]
                    .replace("\xa0", " ")
                )
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2
                city = addr.city
                zip_code = addr.postcode
                if zip_code:
                    zip_code = zip_code.replace("C.P.", "").strip()
            hoo_1 = f"L-V: {poi_data['lunesviernes']}"
            hoo_2 = f"Sabado: {poi_data['sabado']}"
            hoo_3 = f"Domingo: {poi_data['domingo']}"
            hoo = f"{hoo_1}, {hoo_2}, {hoo_3}"

            item = SgRecord(
                locator_domain=domain,
                page_url=poi_data["sitio"],
                location_name=poi["name"],
                street_address=street_address,
                city=city,
                state="",
                zip_postal=zip_code,
                country_code="MX",
                store_number=poi["tid"],
                phone=poi["telefono"],
                location_type="",
                latitude=poi["latitud"],
                longitude=poi["longitud"],
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
