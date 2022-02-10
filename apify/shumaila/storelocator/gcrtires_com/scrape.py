from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    mylist = static_coordinate_list(100, SearchableCountries.USA)
    mylist = mylist + static_coordinate_list(70, SearchableCountries.CANADA)
    daylist = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for lat, lng in mylist:
        url = (
            "https://www.gcrtires.com/bcsutil/commercial/locations?lat="
            + str(lat)
            + "&lon="
            + str(lng)
            + "&radius="
            + "1000"
            + "&bu=tbr&collection=aem_commercial_dealers"
        )

        try:
            loclist = session.get(url, headers=headers).json()
        except:
            continue
        if len(loclist) == 0:
            continue
        for loc in loclist:
            store = loc["locationNo"]
            title = loc["legalName"].replace("\u0026", "&").strip()

            street = loc["streetAddress"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["postalCode"]
            ccode = loc["country"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            phone = loc["businessPhone"]
            phone = phone[0:3] + "-" + phone[4:6] + "-" + phone[6:10]
            hours = ""
            for day in daylist:
                try:
                    if len(loc[day + "Close"]) == 0:
                        hours = hours + day + " Closed "
                        continue
                except:
                    continue
                close = 0
                flag = 0
                try:
                    try:
                        close = int(loc[day + "Close"].split(":", 1)[0])
                    except:
                        close = int(loc[day + "Close"].split(".", 1)[0])
                        flag = 1
                    if close > 12:
                        close = close - 12
                    if flag == 0:
                        hours = (
                            hours
                            + day
                            + " "
                            + loc[day + "Open"]
                            + " am - "
                            + str(close)
                            + ":"
                            + loc[day + "Close"].split(":", 1)[1]
                            + " pm "
                        )
                    elif flag == 1:
                        hours = (
                            hours
                            + day
                            + " "
                            + loc[day + "Open"]
                            + " am - "
                            + str(close)
                            + ":"
                            + loc[day + "Close"].split(".", 1)[1]
                            + " pm "
                        )
                except:
                    hours = hours + day + " Closed "
            try:
                ltype = loc["locationType"]
            except:
                ltype = "<MISSING>"
            link = "https://www.gcrtires.com/stores" + loc["externalPath"]
            if "--" in phone.strip():
                phone = SgRecord.MISSING
            yield SgRecord(
                locator_domain="https://www.gcrtires.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=store,
                phone=phone.strip(),
                location_type=ltype,
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
