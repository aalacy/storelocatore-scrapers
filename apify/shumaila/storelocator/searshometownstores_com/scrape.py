from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
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

    linklist = []
    week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    times = {
        "32400": "9",
        "64800": "6",
        "43200": "12",
        "61200": "5",
        "68400": "7",
        "39600": "11",
        "57600": "4",
        "30600": "8.30",
        "36000": "10",
        "75600": "9",
        "34200": "9:30",
        "46800": "12",
        "45000": "9:30",
        "63000": "5:30",
        "28800": "8",
        "54000": "3",
        "0": "12",
        "50400": "2",
        "66600": "6:30",
        "72000": "8",
        "70200": "7:30",
        "27000": "7:30",
        "73800": "8:30",
        "41400": "11:30",
        "59400": "4:30",
        "21600": "9:00",
        "55800": "3:30",
    }
    zips = static_zipcode_list(radius=100, country_code=SearchableCountries.USA)
    zips = zips + ["36330", "35121", "36301"]

    if True:
        for zip_code in zips:
            search_url = "https://api.searshometownstores.com/lps-mygofer/api/v1/mygofer/store/nearby"
            myobj = {
                "city": "",
                "zipCode": str(zip_code),
                "searchType": "",
                "state": "",
                "session": {
                    "sessionKey": "",
                    "trackingKey": "",
                    "appId": "MYGOFER",
                    "guid": 0,
                    "emailId": "",
                    "userRole": "",
                    "userId": 0,
                },
                "security": {"authToken": "", "ts": "", "src": ""},
            }
            try:
                loclist = session.post(search_url, json=myobj, headers=headers).json()[
                    "payload"
                ]["nearByStores"]
                if len(loclist) > 0:
                    pass
            except:
                continue
            for loc in loclist:
                title = loc["storeName"]
                street = loc["address"]
                city = loc["city"]
                state = loc["stateCode"]
                pcode = loc["zipCode"]
                phone = loc["phone"]
                phone = "(" + phone[0:3] + ") " + phone[3:6] + "-" + phone[6:10]

                store = str(loc["unitNumber"])
                link = (
                    "https://www.searshometownstores.com/home/"
                    + state.lower()
                    + "/"
                    + city.lower().replace(" ", "-")
                    + "/"
                    + store.replace("000", "")
                )
                if link in linklist:
                    continue
                linklist.append(link)

                hourlist = loc["storeDetails"]["strHrs"]

                hours = ""
                for day in week:

                    hours = (
                        hours
                        + day
                        + " "
                        + times[hourlist[day]["opn"]]
                        + " AM - "
                        + times[hourlist[day]["cls"]]
                        + " PM "
                    )
                longt = loc["storeDetails"]["longitude"]
                lat = loc["storeDetails"]["latitude"]
                if len(phone.strip()) < 7:
                    phone = "<MISSING>"
                yield SgRecord(
                    locator_domain="https://www.searshometownstores.com/",
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode.strip(),
                    country_code="US",
                    store_number=str(store),
                    phone=phone.strip(),
                    location_type=SgRecord.MISSING,
                    latitude=str(lat),
                    longitude=str(longt),
                    hours_of_operation=hours,
                )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
