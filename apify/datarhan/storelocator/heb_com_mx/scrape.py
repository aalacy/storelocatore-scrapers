from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.heb.com.mx/tiendas"
    domain = "heb.com.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_data = dom.xpath(
        '//div[h2[strong[contains(text(), "Nuestras Tiendas")]]]/following-sibling::div[@data-element="main"][1]/div//text()'
    )
    all_data = [e.strip() for e in all_data if e.strip()]
    all_data = [e.replace("Horario Consultorio:", "-----") for e in all_data]
    all_data = [
        e.replace("Servicio disponible:", "")
        .replace("Envío a domicilio", "")
        .replace("Pick&Go", "")
        .replace("Lunes a Viernes de 10 a.m. a 2 p.m. y 4 p.m. a 8p.m.", "")
        .replace("Sábado y Domingo de 10 a.m. a 2 p.m.", "")
        .replace("Lunes a Viernes de 10am a 2pm y 4pm a 8pm", "")
        .replace("Sábado de 10am a 2pm", "")
        .replace("Lunes a Sábado de 11am a 8pm", "")
        for e in all_data
    ]
    all_data = [e.strip() for e in all_data if e.strip()]
    all_data = " ;".join(all_data)

    all_locations = all_data.split("----- ;")
    for poi_data in all_locations:
        raw_data = poi_data.split(" ;")[:-1]
        if "Col. " in raw_data[2]:
            raw_data = [raw_data[0]] + [", ".join(raw_data[1:3])] + raw_data[3:]
        raw_address = ", ".join(raw_data[1:]).split("Tel")[0].split("Horario")[0]
        addr = parse_address_intl(raw_address)
        phone = [e for e in raw_data if "Tel" in e]
        phone = phone[0].replace("Tel: ", "").replace("Tel. ", "") if phone else ""
        hoo = [
            e.replace("Horario de tienda:", "")
            for e in raw_data
            if "Horario de tienda" in e
        ][0]
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        state = addr.state
        if state == "Qro.":
            state = ""
        zip_code = addr.postcode
        if zip_code:
            zip_code = zip_code.replace("CP ", "").replace("C.P. ", "")

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=raw_data[0],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
