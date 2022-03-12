from lxml import html
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.boconcept.com/"
    api_url = "https://www.boconcept.com/on/demandware.store/Sites-AF-Site/en_AF/Storelocator-GetStores?topLeftLat=89.9600751224322&topLeftLong=-180&bottomRightLat=-89.24430995711447&bottomRightLong=180&centerLat=64.11066418890735&centerLon=-314.25506842812297"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["stores"]
    for j in js:
        id = j.get("ID")
        page_url = f"https://www.boconcept.com/on/demandware.store/Sites-US-Site/en_US/Storelocator-Detail?storeid={id}"
        location_name = "".join(j.get("name"))
        if location_name.find("salon zamknięty") != -1:
            continue
        location_type = j.get("storeType") or "<MISSING>"
        street_address = (
            f"{j.get('address1')} {j.get('address2')} {j.get('address3')}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        state = str(j.get("stateCode")).replace("None", "").strip() or "<MISSING>"
        if state == "graz@boconcept.at":
            state = "<MISSING>"
        postal = (
            str(j.get("zipCode")).replace(", D I area", "").replace("None", "").strip()
            or "<MISSING>"
        )
        if postal.find("C.P. ") != -1:
            postal = postal.replace("C.P. ", "").strip()
        if (
            postal == "Miraflores"
            or postal == "City Center, Bonifacio Global City"
            or postal == "Sector 1"
            or postal == "Сектор С3, киоск К."
            or postal == "Pozuelo de Alarcón"
        ):
            postal = "<MISSING>"
        if postal.find("MA") != -1:
            postal = postal.replace("MA", "").strip()
        if postal == "東京都中央区日本橋室町2-4-3" or postal == "みなとみらい東急スクエアB2F":
            postal = "<MISSING>"

        city = str(j.get("city")).replace("None", "").strip() or "<MISSING>"

        if postal == "<MISSING>":
            a = parse_address(International_Parser(), street_address)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            city = a.city or "<MISSING>"
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"

        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = str(j.get("phone1")).replace("Tel.", "").strip() or "<MISSING>"
        if phone.find("(Mon-Fri, 10am-5pm)") != -1:
            phone = phone.replace("(Mon-Fri, 10am-5pm)", "").strip()
        phone = phone.replace("＊電話が繋がらない場合はメールにてお問合せください。", "").strip()
        if phone == "＊5/1(金)まではメールにてお問合せください。" or phone == "bc1@boconcept.ru":
            phone = "<MISSING>"
        phone = phone.replace("None", "").strip() or "<MISSING>"

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="store-header__opening-hours"]//table//tr/td/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath('//div[@class="store-header__contact"]/p/text()[1]'))
                .replace("Tel", "")
                .replace(".", "")
                .strip()
                or "<MISSING>"
            )
        if phone.find("＊") != -1:
            phone = phone.split("＊")[0].replace("電話番号", "").strip()
        phone = phone.replace("Tél", "").strip()
        country_code = (
            "".join(tree.xpath('//a[@class="country-selector-toggle modalbox"]/text()'))
            .replace("\n", "")
            .strip()
        )

        if country_code.find("(") != -1:
            country_code = country_code.split("(")[0].strip()
        raw_adr = f"{j.get('address1')} {j.get('address2')} {j.get('city')}, {j.get('stateCode')} {j.get('zipCode')}".replace(
            "None", ""
        ).strip()
        raw_adr = " ".join(raw_adr.split())
        if raw_adr.endswith(",") != -1:
            raw_adr = raw_adr.replace(f"{raw_adr[-1]}", "").strip()

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
