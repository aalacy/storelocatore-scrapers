import re
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.pokeworks.com/"
    api_url = "https://www.pokeworks.com/all-locations"
    session = SgRequests()
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//b[text()="NOW OPEN"]/following::a[contains(@href, "www.pokeworks.com/")]'
    )
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if page_url.find("http") != -1 and page_url.find("https") == -1:
            page_url = page_url.replace("http", "https")
        location_name = "".join(d.xpath(".//text()"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        info = (
            " ".join(tree.xpath('//div[@id="content"]//text()'))
            .replace("\n", "")
            .strip()
        )
        info = " ".join(info.split())
        try:
            ad = info.split("PICKUP & DELIVERY")[1].split("Store")[0].strip()
        except:
            try:
                ad = info.split("STORE INFO")[1].split("Store")[0].strip()
            except:
                ad = info.split("PICKUP")[1].split("Store")[0].strip()
        if ad.find("(") != -1:
            ad = " ".join(ad.split("(")[:-1]).strip()
        ad = ad.replace("TEL:", "").strip()
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        if page_url == "https://www.pokeworks.com/san-luis":
            street_address = "Av. Venustiano Carranza 2065 Cuauhtemoc"
            postal = "78270"
            state = location_name.split(",")[1].strip()
            city = location_name.split(",")[0].strip()
        if page_url == "https://www.pokeworks.com/san-luis-2":
            street_address = "C. Palmira 1070"
            postal = "78295"
            state = location_name.split(",")[1].strip()
            city = location_name.split(",")[0].replace("2", "").strip()
        if page_url == "https://www.pokeworks.com/leon":
            street_address = "Eugenio Garza Sada 1109-local 8 Cumbres del Campestre"
            postal = "37128"
            state = location_name.split(",")[1].strip()
            city = location_name.split(",")[0].replace("2", "").strip()

        try:
            latitude = (
                "".join(tree.xpath("//div/@data-block-json"))
                .split('"mapLat":')[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath("//div/@data-block-json"))
                .split('"mapLng":')[1]
                .split(",")[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        try:
            ph = re.findall(r"[(\d)]{5} [\d]{3}-[\d]{4}", str(info))
        except:
            ph = list("<MISSING>")
        phone = "".join(ph).strip() or "<MISSING>"
        if phone == "<MISSING>" and state != "MX":
            phone = (
                "".join(tree.xpath('//p[./strong[text()="STORE INFO"]]/text()[last()]'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )

        try:
            hours_of_operation = info.split("Hours")[1].strip()
        except:
            try:
                hours_of_operation = info.split("HOURS")[1].strip()
            except:
                hours_of_operation = "<MISSING>"

        if hours_of_operation.find("order") != -1:
            hours_of_operation = hours_of_operation.split("order")[0].strip()
        if hours_of_operation.find("ORDER") != -1:
            hours_of_operation = hours_of_operation.split("ORDER")[0].strip()
        if hours_of_operation.find("Order") != -1:
            hours_of_operation = hours_of_operation.split("Order")[0].strip()
        if hours_of_operation.find("CATERING") != -1:
            hours_of_operation = hours_of_operation.split("CATERING")[0].strip()
        if hours_of_operation.find("Catering") != -1:
            hours_of_operation = hours_of_operation.split("Catering")[0].strip()
        if hours_of_operation.find("catering") != -1:
            hours_of_operation = hours_of_operation.split("catering")[0].strip()
        hours_of_operation = (
            hours_of_operation.replace("-Pickup & Delivery only-", "")
            .replace("-Takeout & Delivery only-", "")
            .strip()
        )
        if hours_of_operation[0] == ":":
            hours_of_operation = " ".join(hours_of_operation.split(":")[1:]).strip()
        if (
            info.find("TEMPORARILY CLOSED") != -1
            or info.find("Temporarily Closed") != -1
        ):
            hours_of_operation = "Temporarily Closed"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
