from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address

session = SgRequests()


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.caferouge.com/"
    api_url = "https://www.caferouge.com/sitemap.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath('//url/loc[contains(text(), "/restaurants/")]')
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        if (
            page_url == "https://www.caferouge.com/restaurants/birmingham/bullring"
            or page_url
            == "https://www.caferouge.com/restaurants/haywards-heath/the-broadway"
        ):
            continue
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h2[@class="restaurant-title"]//text()'))
            or "<MISSING>"
        )
        ad = (
            "".join(tree.xpath('//div[@class="address"]//text()'))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = ad.split(",")[0].strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "UK"
        city = a.city or "<MISSING>"
        if city == "<MISSING>":
            city = location_name
        if location_name == "<MISSING>":
            location_name = city
        text = "".join(tree.xpath('//a[contains(text(), "Get directions")]/@href'))
        try:
            latitude = text.split(",")[-2].split("/")[-1].strip()
            longitude = text.split(",")[-1]
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(tree.xpath('//a[@id="phonenumber"]/text()')) or "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath('//h2[text()="Opening Hours"]/following-sibling::text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.count("CLOSED") == 7:
            hours_of_operation = "CLOSED"

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

    locator_domain = "https://www.caferouge.com/"

    headers = {
        "Authorization": "Bearer 30ad3e38f991a61b137301a74d5a4346f29fa442979b226cbca1a85acc37fc1c",
    }

    params = {
        "content_type": "restaurant",
        "include": "10",
    }

    r = session.get(
        "https://cdn.contentful.com/spaces/6qprbsfbbvrl/environments/master/entries",
        params=params,
        headers=headers,
    )
    js = r.json()["items"]
    for j in js:

        a = j.get("fields")
        page_url = f"https://www.rougebrasserie.com/restaurants/{a.get('city')}/{a.get('slug')}"
        location_name = a.get("title")
        street_address = a.get("addressLine1")
        postal = a.get("postcode")
        country_code = "UK"
        city = a.get("addressCity")
        store_number = a.get("storeId")
        latitude = a.get("addressLocation").get("lat")
        longitude = a.get("addressLocation").get("lon")
        phone = a.get("phoneNumber")
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="opening-hours"]/text()'))
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
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address}, {city}, {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
