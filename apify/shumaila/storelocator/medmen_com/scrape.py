from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    headers = {
        "Sec-Fetch-Mode": "cors",
        "Origin": "https://www.medmen.com",
        "X-Contentful-User-Agent": "sdk contentful.js/0.0.0-determined-by-semantic-release; platform browser; os macOS;",
        "Authorization": "Bearer 3a1fbd8bd8285a5ebe9010b17959d62fed27abc42059373f3789023bb7863a06",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.medmen.com/stores",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "DNT": "1",
    }
    params = (("content_type", "store"),)
    storeslist = session.get(
        "https://cdn.contentful.com/spaces/1ehd3ycc3wzr/environments/master/entries",
        headers=headers,
        params=params,
    ).json()["items"]
    for store in storeslist:
        store = store["fields"]
        if "comingSoon" not in store.keys() or not store["comingSoon"]:
            link = "https://www.medmen.com/stores/" + store["slug"]
            location_id = store["securityId"]
            title = store["name"]
            try:
                street = store["address"]
                city, state = store["address2"].split(", ", 1)
                state, pcode = state.lstrip().split(" ", 1)
            except:
                street, city, state = store["address"].split(", ")
                state, pcode = state.lstrip().split(" ", 1)
            phone = store["phoneNumber"]
            if "Check" in phone:
                phone = "<MISSING>"
            lat = store["location"]["lat"]
            longt = store["location"]["lon"]
            hours = store["storeHours"]
            try:
                if "Sun " in store["storeHours2"]:
                    hours = hours + " " + store["storeHours2"]
            except:
                pass
            if location_id.isdigit():
                pass
            else:
                location_id = "<MISSING>"
            yield SgRecord(
                locator_domain="https://www.medmen.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=str(location_id),
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours.replace("|", " ").strip(),
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
