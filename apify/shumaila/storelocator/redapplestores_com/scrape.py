import json
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

    statelist = [
        "AB",
        "BC",
        "MB",
        "NB",
        "NL",
        "NT",
        "NS",
        "NU",
        "ON",
        "PE",
        "QC",
        "SK",
        "YT",
    ]

    for state in statelist:
        url = (
            "https://www.redapplestores.com/ajax_store.cfm?province="
            + state
            + "&action=cities"
        )
        try:
            loclist = session.get(url, headers=headers).json()["data"]
        except:
            continue
        for loc in loclist:

            link = "https://www.redapplestores.com" + loc["val"]

            r = session.get(link, headers=headers)

            content = r.text.split('"locations":[', 1)[1].split("],", 1)[0]
            content = json.loads(content)
            ccode = content["country"]
            pcode = content["postalzip"]
            lat = content["lat"]
            longt = content["lon"]
            city = content["city"]
            phone = content["phone"]
            street = content["address"]
            title = (
                r.text.split('{"meta":{"title":"', 1)[1].split('"', 1)[0]
                + " - "
                + city
                + ", "
                + state.upper()
            )
            hourlist = (
                r.text.split('"google_structured_data":"', 1)[1]
                .split('}"', 1)[0]
                .replace("\\", "")
                + "}"
            )
            hourlist = json.loads(hourlist)
            hourlist = hourlist["openingHoursSpecification"]
            hours = ""
            for hr in hourlist:

                day = hr["dayOfWeek"][0]
                if day in hours:
                    continue
                opentime = hr["opens"]
                closetime = hr["closes"]
                close = (int)(closetime.split(":", 1)[0])
                if close > 12:
                    close = close - 12
                hours = (
                    hours
                    + day
                    + " "
                    + opentime
                    + " AM - "
                    + str(close)
                    + ":"
                    + closetime.split(":", 1)[1]
                    + " PM "
                )
            store = link.split("/store/", 1)[1].split("/", 1)[0]

            yield SgRecord(
                locator_domain="https://www.redapplestores.com",
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
