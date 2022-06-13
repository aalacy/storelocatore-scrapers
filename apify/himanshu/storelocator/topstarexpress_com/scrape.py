from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("topstarexpress_com")


session = SgRequests()


def fetch_data():
    locator_domain = "https://www.topstarexpress.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    url = "https://www.topstarexpress.com/wp-admin/admin-ajax.php"

    querystring = {
        "action": "get_stores",
        "lat": "",
        "lng": "",
        "radius": "10000000000",
        "categories[0]": "",
    }

    payload = '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="action"\r\n\r\nget_stores\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="lat"\r\n\r\n40.7998227\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="lng"\r\n\r\n-73.65096219999998\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="radius"\r\n\r\n1000\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="categories%5B0%5D"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--'
    headers = {
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        "accept": "text/html, */*; q=0.01",
        "cache-control": "no-cache",
        "postman-token": "a1d955b6-8ac9-15bc-edf1-4dbed597f8ae",
    }

    response = session.post(url, data=payload, headers=headers, params=querystring)

    json_data = response.json()
    for loc in json_data:
        store_number = json_data[loc]["ID"].strip()
        location_name = json_data[loc]["na"].strip()
        page_url = json_data[loc]["gu"].strip()
        latitude = json_data[loc]["lat"].strip()
        longitude = json_data[loc]["lng"].strip()
        street_address = json_data[loc]["st"].strip()
        city = json_data[loc]["ct"].strip()
        zipp = json_data[loc]["zp"].strip()
        phone = json_data[loc]["te"].strip()
        r1 = session.get(page_url)
        soup_r1 = BeautifulSoup(r1.text, "lxml")
        address = soup_r1.find("div", class_="store_locator_single_address")
        list_address = list(address.stripped_strings)
        state = list_address[-1].split(",")[-1].split()[0].strip()
        hours = soup_r1.find("div", class_="store_locator_single_opening_hours")
        if hours is not None:
            list_hours = list(hours.stripped_strings)
            hours_of_operation = " ".join(list_hours).strip()
        else:
            hours_of_operation = "<MISSING>"

        hours_of_operation = (
            hours_of_operation.replace("Opening Hours", "")
            if hours_of_operation
            else "<MISSING>"
        )

        yield SgRecord(
            page_url=page_url,
            store_number=store_number,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
