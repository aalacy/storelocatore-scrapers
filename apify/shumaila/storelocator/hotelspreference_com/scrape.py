from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "authority": "hotelspreference.com",
    "method": "GET",
    "path": "/api/search_hotel?language=en&meeting=0",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "text/plain",
    "cookie": 'PHPSESSID=6q38quk8scrkm2a5lrnblblne7; _ga=GA1.2.1149899697.1640187773; klaro={"app_analytics":true,"app_marketing":true,"app_preference":true,"app_basics":true}; visitor_id798833=323956479; visitor_id798833-hash=ef25a0f48456a6889835918848558ca0e2bc40870644b25973659f53095a4332f38b98ca9c3e19fcda6e337a6521cd3f14a96a6a; _fbp=fb.1.1640187803818.1599214929; _gid=GA1.2.1752607337.1640453373; hpm-visitsDates=2021-12-22 2021-12-25; notificationsDisplayed=%5Bnull%5D; hpm-pageViewd=https://hotelspreference.com/en/maison-albar-hotels-le-diamond_492 https://hotelspreference.com/en#search https://hotelspreference.com/en/madulkelle-tea-eco-lodge_514; _gat_UA-1421733-1=1',
    "referer": "https://hotelspreference.com/en",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
}


def fetch_data():

    url = "https://hotelspreference.com/api/search_hotel?language=en&meeting=0"
    loclist = session.get(url, headers=headers).json()["data"]
    for loc in loclist:

        store = loc["id"]
        link = "https://hotelspreference.com/en/" + loc["slug"] + "_" + str(store)
        title = loc["name"]

        street = loc["location"]["address"]
        city = loc["location"]["city"]
        state = loc["location"]["state"]
        pcode = loc["location"]["zip"]
        ccode = loc["location"]["country_code"]
        lat = loc["location"]["latlng"][0]
        longt = loc["location"]["latlng"][1]

        r = session.get(link, headers=headers)
        try:
            phone = r.text.split('<span itemprop="telephone">', 1)[1].split("<", 1)[0]
        except:
            try:
                phone = (
                    r.text.split('<span id="unclickable">', 1)[1]
                    .split("<", 1)[0]
                    .strip()
                )
            except:
                phone = "<MISSING>"
        yield SgRecord(
            locator_domain="https://hotelspreference.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
