from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mandco.com/"
    api_url = "https://www.mandco.com/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(
        tree.xpath('//script[contains(text(), "app.stores.addSimpleMarker(")]/text()')
    ).split("app.stores.addSimpleMarker(")[1:]
    for d in div:
        location_name = (
            d.split(",")[2]
            .replace("&#40;", "(")
            .replace("&#41;", ")")
            .replace("'", "")
            .strip()
        )
        latitude = d.split(",")[0].replace("'", "").strip()
        longitude = d.split(",")[1].replace("'", "").strip()
        page_url = "https://www.mandco.com/stores"

        data = {
            "dwfrm_storelocator_searchLatitude": f"{latitude}",
            "dwfrm_storelocator_searchLongitude": f"{longitude}",
            "dwfrm_storelocator_searchString": f"{location_name}",
        }

        r = session.post(
            "https://www.mandco.com/on/demandware.store/Sites-mandco-Site/default/Stores-FindBySearchString",
            headers=headers,
            data=data,
        )
        tree = html.fromstring(r.text)
        div_1 = tree.xpath(f'//div[./div[@data-storename="{location_name}"]]')
        for b in div_1:
            info = b.xpath('.//div[@class="storelocation-store-details"]/text()')
            info = list(filter(None, [a.strip() for a in info]))
            ad = " ".join(info[:-1]).replace("\n", "").replace("\r", "").strip()
            ad = " ".join(ad.split())
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "UK"
            city = a.city or "<MISSING>"
            if city == "<MISSING>":
                city = location_name
            if postal == "<MISSING>":
                postal = "".join(info[-2]).strip()
            phone = "".join(info[-1]).strip()
            hours_of_operation = (
                " ".join(b.xpath('.//div[@class="opening-times"]/p//text()'))
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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
