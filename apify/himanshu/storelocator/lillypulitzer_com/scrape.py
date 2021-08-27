from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.lillypulitzer.com/stores/?showMap=true&horizontalView=true&isForm=true",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    rs = "https://www.lillypulitzer.com/on/demandware.store/Sites-lillypulitzer-sfra-Site/default/Stores-FindStores?showMap=true&storeType=ALL_STORES&radius=10000&latitude=39.5243169&longitude=-99.1421644"
    r = session.get(rs, headers=headers)
    data = r.json()["stores"]

    for store_data in data:

        store_number = store_data["ID"]
        slug = store_data["city"]
        if "Lilly" in store_data["storeType"]:
            location_type = store_data["storeType"]
        else:
            location_type = "Other Lilly Destinations"
        location_name = store_data["name"]
        address2 = ""
        if store_data["address2"] is not None:
            address2 = store_data["address2"]
        ad = store_data["address1"] + " " + address2
        a = parse_address(USA_Best_Parser(), ad)
        street_address = "".join(a.street_address_1)
        if not street_address[0].isdigit():
            for s in street_address:
                if s.isdigit():
                    ind = street_address.index(s)
                    street_address = street_address[ind:]
                    break

        city = store_data["city"]

        state = store_data["stateCode"]

        postal = (
            store_data["postalCode"] if store_data["postalCode"] != "" else "<MISSING>"
        )
        country_code = store_data["countryCode"]
        phone = store_data["phone"] if store_data["phone"] != "" else "<MISSING>"
        latitude = store_data["latitude"]
        longitude = store_data["longitude"]
        hours = ""
        store_hours = store_data["customStoreHours"]
        for key in store_hours:
            hours = hours + " " + key["day"] + " " + key["hours"]
        hours_of_operation = hours.strip() if hours != "" else "<MISSING>"
        if hours_of_operation.count("CLOSED") == 7:
            hours_of_operation = "Closed"
        page_url = (
            "https://www.lillypulitzer.com/store/details/?storeId="
            + store_number
            + "&city="
            + slug
        )

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.lillypulitzer.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
