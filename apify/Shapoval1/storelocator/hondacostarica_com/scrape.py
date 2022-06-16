from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://hondacostarica.com/"
    page_urls = [
        "https://www.hondacostarica.com/localiza-tu-sucursal",
        "https://hondaelsalvador.com/localiza-tu-sucursal",
        "https://www.hondahonduras.com/localiza-tu-sucursal",
    ]
    for page_url in page_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="locations"]/div')
        for d in div:
            info = d.xpath(".//address/p/text()")
            info = list(filter(None, [a.strip() for a in info]))
            location_name = (
                "".join(d.xpath('.//span[@class="Service-locator_name"]/text()'))
                .replace("\n", "")
                .strip()
            )
            ad = []
            for i in info:
                if "Dirección" in i or "Blvd" in i:
                    ad.append(i)
            adr = (
                " ".join(ad)
                .replace("\n", "")
                .replace("\r", "")
                .replace("Dirección:", "")
                .strip()
            )
            a = parse_address(International_Parser(), adr)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            if postal == "<MISSING>":
                for b in info:
                    if "Postal" in b:
                        postal = "".join(b).split("Postal")[1].strip()
            country_code = page_url.split("honda")[1].split(".")[0].capitalize().strip()
            if country_code == "Costarica":
                country_code = "CR"
            if country_code == "Elsalvador":
                country_code = "SV"
            if country_code == "Honduras":
                country_code = "HN"
            city = location_name
            if city.find("FACO") != -1:
                city = city.split("FACO")[1].strip()
            if city.find("Grupo Q") != -1:
                city = city.split("Grupo Q")[1].strip()
            if city.find("Honda") != -1:
                city = city.split("Honda")[1].strip()
            latitude = "".join(d.xpath(".//@data-lat"))
            longitude = "".join(d.xpath(".//@data-lng"))
            phone = "<MISSING>"
            for i in info:
                if "Telefónica" in i:
                    phone = "".join(i).split("Telefónica:")[1].strip()
                if "Venta de autos:" in i:
                    phone = "".join(i).split("Venta de autos:")[1].strip()
            if phone.find("y") != -1:
                phone = phone.split("y")[0].strip()
            hours_lst = []
            for i in info:
                if "Horario:" in i or "Sábados" in i:
                    hours_lst.append(i)
            hours_of_operation = (
                " ".join(hours_lst).replace("\n", "").replace("Horario:", "").strip()
                or "<MISSING>"
            )

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
