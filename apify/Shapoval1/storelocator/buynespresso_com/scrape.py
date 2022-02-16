import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.buynespresso.com/"
    api_urls = [
        "https://www.buynespresso.com/mu_en/shopfinder",
        "https://www.buynespresso.com/jo_en/shopfinder",
        "https://www.buynespresso.com/eg_en/shopfinder",
        "https://ma.buynespresso.com/ma_en/shopfinder",
        "https://za.buynespresso.com/za_en/shopfinder.html",
        "https://www.buynespresso.com/jo_en/shopfinder",
        "https://www.buynespresso.com/lb_en/shopfinder",
        "https://www.buynespresso.com/om_en/shopfinder",
        "https://sa.buynespresso.com/sa_en/shopfinder.html",
        "https://www.buynespresso.com/qa_en/shopfinder",
        "https://kw.buynespresso.com/kw_en/shopfinder",
        "https://ae.buynespresso.com/ae_en/shopfinder",
    ]
    for api_url in api_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)

        tree = html.fromstring(r.text)
        div = (
            "".join(
                tree.xpath(
                    '//script[contains(text(), "mapsData.shopDescriptions")]/text()'
                )
            )
            .split("mapsData.shopDescriptions =")[1]
            .split("mapsData.storesLatLng")[0]
            .strip()
        )
        div = "".join(div[:-1])
        js = json.loads(div)
        for j in js:
            b = j.get("description")
            page_url = api_url
            location_name = b.get("shop_name") or "<MISSING>"
            street_address = (
                "".join(b.get("street")).replace("\n", " ").strip() or "<MISSING>"
            )
            state = "<MISSING>"
            postal = b.get("postcode") or "<MISSING>"
            if postal == "n/a" or postal.find("Cairo") != -1 or postal == "N/A":
                postal = "<MISSING>"
            country_code = page_url.split(".com/")[1].split("_")[0].upper().strip()
            city = b.get("city") or "<MISSING>"
            if city == "Kuwat City":
                city = "Kuwait City"
            if street_address.find(f" {city}") != -1:
                street_address = (
                    street_address.split(f" {city}")[0].replace(",", "").strip()
                )
            phone = b.get("telephone") or "<MISSING>"
            if phone == "n/a":
                phone = "<MISSING>"
            hours = b.get("other_opentimes_info") or "<MISSING>"
            hours_of_operation = "<MISSING>"
            if hours != "<MISSING>":
                a = html.fromstring(hours)
                hours_of_operation = (
                    " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split())
            if hours_of_operation.find("Opening times may") != -1:
                hours_of_operation = hours_of_operation.split("Opening times may")[
                    0
                ].strip()
            if hours_of_operation.find("Public Holiday") != -1:
                hours_of_operation = hours_of_operation.split("Public Holiday")[
                    0
                ].strip()

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
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

    locator_domain = "https://www.buynespresso.com/"
    countries = ["UK", "BE", "CH", "NO"]
    for c in countries:
        session = SgRequests()
        r = session.get(
            f"https://www.nespresso.com/storelocator/app/find_poi-v4.php?country={c}"
        )
        js = r.json()
        for j in js:
            a = j.get("point_of_interest")
            location_type = a.get("type") or "<MISSING>"
            street_address = a.get("address").get("address_line")
            city = a.get("address").get("city").get("name")
            postal = "".join(a.get("address").get("postal_code"))
            location_name = (
                a.get("address")
                .get("name")
                .get("company_name_type")
                .get("name")
                .get("name")
                or "<MISSING>"
            )
            phone = a.get("phone") or "<MISSING>"
            hours_of_operation = (
                "".join(a.get("opening_hours_text").get("text"))
                .replace("<br>", " ")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = (
                hours_of_operation.replace("The opening hours are;", "")
                .replace("Opening hours are;", "")
                .replace("<br />", " ")
                .replace("<br", "")
                .replace("&oslash;:", "ø")
                .strip()
            )
            if hours_of_operation.find("Horaires spéciaux") != -1:
                hours_of_operation = hours_of_operation.split("Horaires spéciaux")[
                    0
                ].strip()
            if hours_of_operation.find("Orari speciali ") != -1:
                hours_of_operation = hours_of_operation.split("Orari speciali ")[
                    0
                ].strip()
            if hours_of_operation.find("zielle Öffnungszeiten") != -1:
                hours_of_operation = hours_of_operation.split("zielle Öffnungszeiten")[
                    0
                ].strip()
            if hours_of_operation.find("Boutique-Bereich:") != -1:
                hours_of_operation = (
                    hours_of_operation.split("Boutique-Bereich:")[1]
                    .split("Spezielle")[0]
                    .strip()
                )
            if hours_of_operation.find("Spezielle Öffnungszeiten") != -1:
                hours_of_operation = hours_of_operation.split(
                    "Spezielle Öffnungszeiten"
                )[0].strip()
            hours_of_operation = (
                hours_of_operation.replace("Öffunungszeiten:", "")
                .replace("öffunungszeiten:", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
            latitude = j.get("position").get("latitude")
            longitude = j.get("position").get("longitude")
            page_url = f"https://www.nespresso.com/{c.lower()}/en/store-locator"
            country_code = c
            if postal.find(" ") != -1 and country_code == "CH":
                postal = postal.split()[0].strip()

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
