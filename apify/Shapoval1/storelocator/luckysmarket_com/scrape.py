import datetime
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.luckysmarket.com/"
    api_url = "https://www.luckysmarket.com/contact-us"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[@style="font-size:16px; line-height:1.7em;"]')
    for d in div:

        ad = "".join(d.xpath(".//following-sibling::p[2]//text()")).replace(
            "3960 3990", "3990"
        )
        street_address = ad.split(",")[0].strip()
        country_code = "US"
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        city = ad.split(",")[1].strip()
        phone = "".join(d.xpath(".//following-sibling::p[1]//text()"))
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "".join(d.xpath(".//following-sibling::p[3]//text()"))
        location_name = "".join(d.xpath(".//text()"))
        slug = (
            location_name.replace("Lucky's Market", "")
            .replace("Lucky's", "")
            .replace(",", "")
            .split()[0]
            .upper()
            .strip()
        )

        page_urls = d.xpath(
            f'.//preceding::p[text()="STORES"]/following::ul[1]/li/a[contains(text(), "{slug}")][1]/@href'
        )
        page_url = "".join(page_urls[-1])
        session = SgRequests()

        api_url = "https://api.freshop.com/1/stores?app_key=luckys_market&has_address=true&limit=100&token={}"
        d = datetime.datetime.now()
        unixtime = datetime.datetime.timestamp(d) * 1000
        frm = {
            "app_key": "luckys_market",
            "referrer": "https://www.luckysmarket.com/",
            "utc": str(unixtime).split(".")[0],
        }
        r = session.post("https://api.freshop.com/2/sessions/create", data=frm).json()
        token = r["token"]

        r = session.get(api_url.format(token))
        js = json.loads(r.text)
        for j in js["items"]:
            adr = "".join(j.get("address_1")).split()[0].strip()
            if street_address.find(f"{adr}") != -1:
                latitude = j.get("latitude")
                longitude = j.get("longitude")
                store_number = j.get("store_number")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
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
