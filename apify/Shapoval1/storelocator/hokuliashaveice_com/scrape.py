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
    div = (
        "".join(tree.xpath('//script[contains(text(), "roadmap")]/text()'))
        .split("var features = [")[1]
        .split("];")[0]
        .split("position:")[1:]
    )

    for d in div:

        ht_block = d.split("message:")[1].split("}")[0].strip()
        a = html.fromstring(ht_block)
        info = a.xpath("//*//text()")
        info = list(filter(None, [a.strip() for a in info]))
        location_name = "".join(info[0]).replace('"', "").strip()
        ad = " ".join(info[1:4]).replace('"', "").strip()

        if ad.find("Hours") != -1:
            ad = ad.split("Hours")[0].strip()
        phone_list = re.findall(
            re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), ad
        )
        sub_phone = "".join(phone_list).strip() or "<MISSING>"
        if ad.find(f"{sub_phone}") != -1:
            ad = ad.split(f"{sub_phone}")[0].strip()
        if ad.find("http") != -1:
            ad = ad.split("http")[0].strip()
        if ad.find("Mon") != -1:
            ad = ad.split("Mon")[0].strip()
        if ad.find("opening") != -1:
            ad = ad.split("opening")[0].strip()
        ad = ad.replace("Check for Seasonal", "").replace("sdfasdf", "").strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        adr = " ".join(info)
        ph_list = re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), adr)
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if d.find("LatLng") != -1:
            latitude = d.split("LatLng(")[1].split(",")[0].strip()
            longitude = d.split("LatLng(")[1].split(",")[1].split(")")[0].strip()
        phone = "".join(ph_list) or "<MISSING>"
        if phone == "832-548-0988832-548-0988":
            phone = "832-548-0988"

        tmp = []
        for i in info:
            if (
                "12pm-9pm" in i
                or "PM" in i
                or "-9p" in i
                or "Mon" in i
                or "8pm" in i
                or "pm" in i
                or "Closed" in i
            ):
                tmp.append(i)
        hours_of_operation = " ".join(tmp) or "<MISSING>"
        if hours_of_operation.find("Hours:") != -1:
            hours_of_operation = hours_of_operation.replace(
                "Hours: M-Th12-7p & F-Sun 12-8pm 12-7 pm", ""
            ).strip()
        ht_info = tree.xpath(f'//div[contains(text(), "{location_name}")]//text()')
        ht_info = list(filter(None, [a.strip() for a in ht_info]))
        ht_i = " ".join(ht_info)
        location_type = "<MISSING>"
        if "Coming soon" in ht_i:
            location_type = "Coming soon"
        if "Closed for the season" in ht_i:
            location_type = "Temporarily Closed"

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
