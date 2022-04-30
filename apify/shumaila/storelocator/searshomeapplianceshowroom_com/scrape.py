from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
    "content-type": "application/json",
    "accept": "application/json, text/plain, */*",
}


def fetch_data():

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    for statenow in states:
        url = (
            "https://api.searshometownstores.com/lps-mygofer/api/v1/mygofer/store/getStoreDetailsByState?state="
            + statenow
        )

        loclist = session.get(url, headers=headers).json()["payload"]["stores"]
        for loc in loclist:
            title = loc["storeName"]
            pcode = loc["zipCode"]
            city = loc["city"]
            state = loc["stateCode"]
            street = loc["streetAddress"]
            phone = loc["phoneNumber"]
            hours = (
                "Mon "
                + loc["monHrs"]
                + " Tue "
                + loc["tueHrs"]
                + " Wed "
                + loc["wedHrs"]
                + " Thu "
                + loc["thrHrs"]
                + " Fri "
                + loc["friHrs"]
                + " Sat "
                + loc["satHrs"]
                + " Sun "
                + loc["sunHrs"]
            )
            search_url = "https://api.searshometownstores.com/lps-mygofer/api/v1/mygofer/store/nearby"
            myobj = {
                "city": "",
                "zipCode": str(pcode),
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
            store = lat = longt = link = "<MISSING>"
            try:
                locnow = session.post(search_url, json=myobj, headers=headers).json()[
                    "payload"
                ]["nearByStores"]
                for div in locnow:
                    if (
                        city.upper() + " - AUTH HOMETOWN" == div["storeName"]
                        or phone.replace("(", "")
                        .replace(")", "")
                        .replace("-", "")
                        .replace(" ", "")
                        .replace(".", "")
                        == div["phone"]
                    ):
                        store = str(div["unitNumber"])
                        link = (
                            "https://www.searshomeapplianceshowroom.com/home/"
                            + state.lower()
                            + "/"
                            + city.lower()
                            + "/"
                            + store.replace("000", "")
                        )
                        longt = div["storeDetails"]["longitude"]
                        lat = div["storeDetails"]["latitude"]
                        break
            except:
                continue
            yield SgRecord(
                locator_domain="https://www.searshomeapplianceshowroom.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="US",
                store_number=store,
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=lat,
                longitude=longt,
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
