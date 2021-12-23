from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.imocarwash.com"
    api_url = "https://www.imocarwash.com/gb/search-results/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@id="countrySelect"]/option')
    for d in div:
        slug = "".join(d.xpath(".//@value")).split("/")[0].upper()

        session = SgRequests()
        r = session.get(
            f"https://www.imocarwash.com/umbraco/api/location/get?country={slug}",
            headers=headers,
        )
        js = r.json()["Markers"]
        for j in js:

            page_url = f"https://www.imocarwash.com/{j.get('Url')}"
            location_name = j.get("Name") or "<MISSING>"
            ad = "".join(j.get("Address")) or "<MISSING>"
            if ad == ",  ":
                ad = "<MISSING>"
            street_address = "<MISSING>"
            if ad != "<MISSING>":
                a = parse_address(International_Parser(), ad)
                street_address = (
                    f"{a.street_address_1} {a.street_address_2}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
                if street_address == "<MISSING>":
                    street_address = "".join(j.get("Address"))
            postal = "".join(j.get("Postcode")) or "<MISSING>"
            country_code = j.get("Country") or "<MISSING>"
            if country_code == "AU" and postal.find(" ") != -1:
                postal = postal.split()[1].strip()
            city = j.get("City") or "<MISSING>"
            store_number = j.get("Id") or "<MISSING>"
            latitude = j.get("Latitude") or "<MISSING>"
            longitude = j.get("Longitude") or "<MISSING>"
            phone = j.get("Phone") or "<MISSING>"
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(
                    tree.xpath('//div[@class="location-content__hours"]/time/@datetime')
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
