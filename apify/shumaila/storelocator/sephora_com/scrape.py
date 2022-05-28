from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
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

    mylist = static_coordinate_list(100, SearchableCountries.USA)
    mylist = mylist + static_coordinate_list(100, SearchableCountries.CANADA)

    daylist = ["mon", "tues", "wednes", "thurs", "fri", "satur", "sun"]
    for lat, lng in mylist:
        url = (
            "https://www.sephora.com/api/util/stores?latitude="
            + str(lat)
            + "&longitude="
            + str(lng)
            + "&radius=100&autoExpand=0"
        )
        try:
            loclist = session.get(url, headers=headers).json()["stores"]
        except:
            continue
        for loc in loclist:
            title = "Sephora " + loc["displayName"]
            street = loc["address"]["address1"] + " " + str(loc["address"]["address2"])
            city = loc["address"]["city"]
            state = loc["address"]["state"]
            pcode = loc["address"]["postalCode"]
            ccode = loc["address"]["country"]
            phone = str(loc["address"]["phone"])
            lat = loc["latitude"]
            longt = loc["longitude"]
            store = loc["storeId"]
            link = "https://www.sephora.com" + loc["targetUrl"]

            hours = ""
            try:
                hourslist = loc["storeHours"]
                for day in daylist:

                    hours = hours + day + "day " + hourslist[day + "dayHours"] + " "
                if len(hours) < 3:
                    hours = "<MISSING>"
                if len(phone) < 3:
                    phone = "<MISSING>"
                hours = (
                    hours.replace("day", "day ")
                    .replace("PM", "PM ")
                    .replace("AM", "AM ")
                    .replace("osed", "osed ")
                    .strip()
                )
            except:
                hours = "Opening Soon"
            if ("AM " and "PM ") not in hours and "Opening Soon" not in hours:
                hours = "<MISSING>"
            if (" sunday " not in hours) and ("<MISSING>" not in hours):
                hours = hours + " sunday Closed "
            hours = hours.replace("sunday sunday Closed ", "sunday Closed ")
            yield SgRecord(
                locator_domain="https://www.sephora.com/",
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
