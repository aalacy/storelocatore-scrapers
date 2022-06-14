from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):
    session = SgRequests()
    r = session.get("https://www.morningsunhealthfoods.ca/locations")
    tree = html.fromstring(r.text)
    block_key = (
        "".join(tree.xpath('//script[contains(text(), "static/js")]/text()'))
        .split("static/js/")[1]
        .split("+{")[1]
        .split("}")[0]
        .strip()
    )
    keys = block_key.split(",")
    for k in keys:

        key = str(k).replace(":", ".").replace('"', "").strip()
        api_url = f"https://www.morningsunhealthfoods.ca/static/js/{key}.chunk.js"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        try:
            jsblock = (
                r.text.split("features:")[1]
                .split("},p=t")[0]
                .replace("!0", "0")
                .strip()
            )
        except:
            continue

        js = jsblock.split("{geometry:")
        for j in js:
            if j == "[":
                continue

            page_url = "https://www.morningsunhealthfoods.ca/locations"
            location_name = j.split('location:"')[1].split('"')[0].strip()
            ad = (
                j.split('address:"')[1]
                .split('"')[0]
                .replace(", #313", " #313,")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "CA"
            city = a.city or "<MISSING>"
            phone = j.split('phone:"')[1].split('"')[0].strip()
            hours_of_operation = (
                j.split("hours:")[1]
                .split("}}")[0]
                .replace("{", "")
                .replace(":", " ")
                .replace('"', "")
                .replace(" 30", ":30")
                .strip()
            )
            if "permanentlyClosed" in j:
                hours_of_operation = "Permanently Closed"

            longitude = j.split("coordinates:[")[1].split(",")[0].strip()
            latitude = j.split("coordinates:[")[1].split(",")[1].split("]")[0].strip()

            location_type = j.split('category:"')[1].split('"')[0].strip()
            location_type = (
                location_type.replace("ahc", "Alive Health Centre")
                .replace("ms", "Morning Sun Health Foods")
                .replace("sp", "Supplements Plus")
            )
            if location_type != "Morning Sun Health Foods":
                continue
            if hours_of_operation == "Permanently Closed":
                continue

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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.morningsunhealthfoods.ca"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
