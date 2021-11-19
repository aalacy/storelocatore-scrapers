from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.mcdonalds.com.tr/restaurants/getstores"
    domain = "mcdonalds.com.tr"
    hdr = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "MCID=AAAAAAVXj7xyACrnKXPpfe3d9cBBFwbazoe8zSHlbNXOwj7Hww==; _cowaCorp=; __RequestVerificationToken=y-y2LpM4xXYAsWP6Z8L7f9TThqe2MF7HQmYv6N8-X5yGpcmQDQvvSKi8QszwN15TXpTe8nUrmUeYB6sVKP9CX5utWKA0-t5c7PlNbKkl8dY1; _gcl_au=1.1.1944422003.1629476882; _gid=GA1.3.1096461901.1629476883; _fbp=fb.2.1629476883178.385547873; _hjid=9e7ac3d1-b3fe-4763-98f7-aabdfc5bf92f; _hjFirstSeen=1; _ym_uid=1629476884119046768; _ym_d=1629476884; _ym_isad=2; _hjAbsoluteSessionInProgress=0; _ym_visorc=w; cookie-policy=true; ASP.NET_SessionId=sywsscugk3jwptytstnird02; _ga=GA1.3.1998144360.1629476883; _gat_UA-1698196-13=1; _ga_H4Z1720GTW=GS1.1.1629476881.1.1.1629477589.60",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    frm = "cityId=0&subcity=&avm=false&birthday=false&isDeliveryStore=false&open724=false&breakfast=false&mcdcafe=false"
    data = session.post(start_url, headers=hdr, data=frm).json()

    all_locations = data["data"]
    for poi in all_locations:
        addr = parse_address_intl(poi["STORE_ADDRESS"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hours_of_operation = (
            f"{poi['STORE_OPEN_AT']['Hours']}:00 - {poi['STORE_CLOSE_AT']['Hours']}:00"
        )
        city_raw = poi["STORE_ADDRESS"].split("/")[-1].strip()
        addr = parse_address_intl(city_raw)
        city = addr.city
        zip_code = addr.postcode
        if city and city.split()[-1].isnumeric():
            city = " ".join(city.split()[:-1])
        if city == "C-10-11":
            street_address += " C-10-11"
            city = "Antalya"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["STORE_NAME"],
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=zip_code,
            country_code=addr.country,
            store_number=poi["STORE_ID"],
            phone=poi["STORE_PHONE"],
            location_type=SgRecord.MISSING,
            latitude=poi["LATITUDE"],
            longitude=poi["LONGITUDE"],
            hours_of_operation=hours_of_operation,
            raw_address=poi["STORE_ADDRESS"].replace("\n", " ").strip(),
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
