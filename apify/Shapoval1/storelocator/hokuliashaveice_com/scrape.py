import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://hokuliashaveice.com/"
    page_url = "https://hokuliashaveice.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./img[@class="product-icon"]]')[1:]
    for d in div:
        info = d.xpath(".//text()")
        info = list(filter(None, [a.strip() for a in info]))
        info_s = " ".join(info)
        phone_lst = re.findall(
            re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), info_s
        )
        phone = "".join(phone_lst) or "<MISSING>"
        location_name = "".join(info[0]).strip()
        if location_name.find("Year Round Catering") != -1:
            continue
        adr = (
            " ".join(info[1:])
            .replace("Open", "")
            .replace("Coming soon", "")
            .replace("sdfasdf", "")
            .replace("HokuliaAthens.com", "")
            .replace("Closed for the season", "")
            .strip()
        )
        hours_of_operation = "<MISSING>"
        if adr.find("http") != -1:
            adr = adr.split("http")[0].strip()
        if adr.find(f"{phone}") != -1:
            adr = adr.split(f"{phone}")[0].strip()
        if "Coming soon" in info_s:
            hours_of_operation = "Coming Soon"
        if "Closed for the season" in info_s:
            hours_of_operation = "Temporarily Closed"
        if "Hours" in adr:
            hours_of_operation = adr.split("Hours:")[1].strip()
            adr = adr.split("Hours")[0].strip()
        if "opening" in adr:
            hours_of_operation = adr.split("from")[1].strip()
            adr = adr.split("opening")[0].strip()
        for i in info:
            if "Daily" in i or "daily" in i:
                hours_of_operation = str(i)
        if hours_of_operation.find("As") != -1:
            hours_of_operation = hours_of_operation.split("As")[0].strip()
        if hours_of_operation.find("from") != -1:
            hours_of_operation = hours_of_operation.split("from")[1].strip()
        adr = (
            adr.replace("Next to Burberry/Blaze Pizza", "")
            .replace("(Inside Walmart)", "")
            .replace("(In front of the HEB)", "")
            .replace("(Fresh Market)", "")
            .replace("(Ft. Union Blvd)", "")
            .replace("(by Burt Bros.)", "")
            .replace("(Fresh Market Parking Lot)", "")
            .replace("(Down East Lot)", "")
            .replace("(By Daylight Donuts)", "")
            .replace("(Near Honeybaked Ham)", "")
            .replace("(Near Smith's Food & Drug)", "")
            .replace("(Dominos Parking Lot)", "")
            .replace("Stars Recreation Center -", "")
            .replace("In Harvey Park by Splashpad", "")
            .strip()
        )
        adr = " ".join(adr.split())
        a = parse_address(International_Parser(), adr)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if location_name.find("426 South Court Street") != -1:
            location_name = "<MISSING>"
            street_address = "426 South Court Street"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if "Am Fork" in street_address:
            city = "Am Fork"
            street_address = street_address.split("Am Fork")[0].strip()
        text = "".join(d.xpath('.//a[contains(@href, "tel")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if latitude == "<MISSING>":
            try:
                latitude = (
                    "".join(
                        tree.xpath(
                            f'//script[contains(text(), "{location_name}")]/text()'
                        )
                    )
                    .split(f"{location_name}")[0]
                    .split("LatLng(")[-1]
                    .split(",")[0]
                    .strip()
                )
                longitude = (
                    "".join(
                        tree.xpath(
                            f'//script[contains(text(), "{location_name}")]/text()'
                        )
                    )
                    .split(f"{location_name}")[0]
                    .split("LatLng(")[-1]
                    .split(",")[1]
                    .split(")")[0]
                    .strip()
                )
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"
        if latitude == "<MISSING>":
            latitude = (
                "".join(
                    tree.xpath(f'//script[contains(text(), "{street_address}")]/text()')
                )
                .split(f"{street_address}")[0]
                .split("LatLng(")[-1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(
                    tree.xpath(f'//script[contains(text(), "{street_address}")]/text()')
                )
                .split(f"{street_address}")[0]
                .split("LatLng(")[-1]
                .split(",")[1]
                .split(")")[0]
                .strip()
            )
        map_info = (
            "".join(tree.xpath(f'//script[contains(text(), "{latitude}")]/text()'))
            .split(f"{longitude}")[1]
            .split("}")[0]
            .strip()
        )
        if phone == "<MISSING>":
            phone_lst = re.findall(
                re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), map_info
            )
            phone = "".join(phone_lst) or "<MISSING>"
        map_info_h = map_info.split('message: "')[1].split('"')[0]
        c = html.fromstring(map_info_h)
        map_info_l = c.xpath("//*//text()")
        map_info_l = list(filter(None, [m.strip() for m in map_info_l]))
        tmp = []
        for x in map_info_l:
            if (
                "Mon" in x
                or "Sun" in x
                or "M-F" in x
                or "Sunday" in x
                or "Fri" in x
                or "12pm-9pm" in x
            ):
                tmp.append(x)
        if hours_of_operation == "<MISSING>":
            hours_of_operation = "; ".join(tmp)

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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
