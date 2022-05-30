import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://rainbowdrivein.com/"
    api_url = "https://www.google.com/maps/d/u/0/embed?mid=1ZrSu9RQvg_anylS-qaRL10tkm57rZTwT&ll=21.354652853702625%2C-157.97386819511723&z=11"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    cleaned = (
        r.text.replace("\\t", " ")
        .replace("\t", " ")
        .replace("\\n]", "]")
        .replace("\n]", "]")
        .replace("\\n,", ",")
        .replace("\\n", "#")
        .replace('\\"', '"')
        .replace("\\u003d", "=")
        .replace("\\u0026", "&")
        .replace("\\", "")
        .replace("\xa0", " ")
        .replace('"[{', "[{")
        .replace('}]"', "}]")
    )
    locations = json.loads(
        cleaned.split('var _pageData = "')[1].split('";</script>')[0]
    )[1][6][0][12][0][13][0]

    for l in locations:
        page_url = "https://rainbowdrivein.com/locations/"
        location_name = l[5][0][1][0]
        slug = str(location_name).split()[0].strip()
        if location_name == "Rainbow Drive-In":
            slug = "3308"
        if str(location_name).find("Pearlridge") != -1:
            slug = "98-1005"
        if location_name == "Rainbow Drive-In Kalihi":
            slug = "1339"

        country_code = "US"
        latitude = l[1][0][0][0]
        longitude = l[1][0][0][1]
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        street_address = (
            "".join(tree.xpath(f'//p[contains(text(), "{slug}")]/text()[1]'))
            .replace("\n", "")
            .strip()
            or location_name
        )
        ad = (
            "".join(tree.xpath(f'//p[contains(text(), "{slug}")]/text()[2]'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>" and street_address == "94-226 Leoku St":
            ad = "Waipahu, HI 96797"
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        location_name = (
            "".join(
                tree.xpath(f'//p[contains(text(), "{slug}")]/preceding::h2[1]//text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        phone = (
            "".join(
                tree.xpath(f'//p[contains(text(), "{slug}")]/following::h6[1]//text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    f'//p[contains(text(), "{slug}")]/following::*[contains(text(), "HOURS")][1]/following::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
