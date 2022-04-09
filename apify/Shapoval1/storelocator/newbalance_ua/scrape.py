from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://newbalance.ua/"
    api_url = "https://newbalance.ua/assets/webpack/js/d63db4.js?v=1648480965"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    cities = [
        "kyiv",
        "dnipro",
        "lviv",
        "kharkiv",
        "odessa",
        "zaporizhia",
        "kryvyiRih",
        "khmelnitsky",
    ]
    stores = r.text.split("t.stores=")[1].split("t.storesPartners")[0]
    for c in cities:
        div = stores.split(f"{c}:")[1].split("}}]}],")[0] + "}}]}]"
        js_block = (
            div.replace("title", '"title"')
            .replace("storesList", '"storesList"')
            .replace("item", '"item"')
            .replace("location", '"location"')
            .replace("lat", '"lat"')
            .replace("lng", '"lng"')
            .replace("info", '"info"')
            .replace("name", '"name"')
            .replace("floor", '"floor"')
            .replace("metroStation", '"metroStation"')
            .replace("phone1", '"phone1"')
            .replace("phone2", '"phone2"')
            .replace("schedule", '"schedule"')
            .replace("adressName", '"adressName"')
            .replace(",adress", ',"adress"')
        )
        if js_block.find("}},24") != -1:
            js_block = js_block.split("}},24")[0].strip()
        js = eval(js_block)
        for j in js:
            locations = j.get("storesList")
            for s in locations:

                page_url = f"https://newbalance.ua/stores?city={c}"
                location_name = "New Balance Concept Shop"
                street_address = "".join(s.get("adressName"))
                if (
                    street_address.find("ТРЦ") != -1
                    or street_address.find("ТЦ") != -1
                    or street_address.find("ТК") != -1
                ):
                    street_address = " ".join(street_address.split(",")[1:]).strip()
                street_address = street_address.replace('"ДИСКОНТ-ФОРМАТ",', "").strip()
                country_code = "UA"
                city = c
                try:
                    latitude = s.get("location").get("lat")
                    longitude = s.get("location").get("lng")
                except:
                    latitude, longitude = "<MISSING>", "<MISSING>"
                phone = s.get("info").get("phone1")
                hours_of_operation = s.get("info").get("schedule")

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=SgRecord.MISSING,
                    zip_postal=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
