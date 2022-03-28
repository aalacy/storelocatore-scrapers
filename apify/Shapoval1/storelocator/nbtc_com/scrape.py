from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://nbtc.com"

    session = SgRequests()
    r = session.get("https://nbtc.com/locations/")
    tree = html.fromstring(r.text)
    key = (
        "".join(tree.xpath('//link[@rel="preload"]/@href'))
        .split("static/")[1]
        .split("/")[0]
        .strip()
    )

    api_url = f"https://nbtc.com/_nuxt/static/{key}/locations/payload.js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    block = (
        r.text.split("branches:")[1].split(",fetch:[]")[0].replace("}]}]", "}]").strip()
    )
    block = (
        block.replace("id:", '"id":')
        .replace("title", '"title"')
        .replace("branchTileLabel", '"branchTileLabel"')
        .replace("apartmentOrSuite", '"apartmentOrSuite"')
        .replace("city", '"city"')
        .replace("state", '"state"')
        .replace("zipcode", '"zipcode"')
        .replace("streetAddress", '"streetAddress"')
    )
    block = (
        block.replace("latitude", '"latitude"')
        .replace("longitude", '"longitude"')
        .replace("phoneNumber", '"phoneNumber"')
        .replace("url:", '"url":')
    )
    block = (
        block.replace(":Q", ':"Q"')
        .replace(":R", ':"R"')
        .replace(":S", ':"S"')
        .replace(":T", ':"T"')
        .replace(":U", ':"U"')
        .replace(":V", ':"V"')
        .replace(":b", ':"B"')
        .replace(":Z", ':"Z"')
    )
    block = (
        block.replace(":W", ':"W"')
        .replace(":X", ':"X"')
        .replace(":Y", ':"Y"')
        .replace(":x", ':"x"')
        .replace(":a", ':"a"')
        .replace(":c", ':"c"')
        .replace(":y", ':"y"')
    )

    js = eval(block)

    for j in js:

        page_url = j.get("url")
        location_name = j.get("title")
        location_type = "Branch"
        street_address = j.get("streetAddress")
        phone = j.get("phoneNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        country_code = "US"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            " ".join(
                tree.xpath(
                    '//h6[text()="Branch Address"]/following-sibling::div//text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        city = ad.split(",")[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h6[contains(text(), "Lobby")]/following-sibling::div/p/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
