from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.simon.com/search"
    Found = True
    while Found:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '{"PropertyType":' in line:
                Found = False
                items = line.split('{"PropertyType":')
                for item in items:
                    if '"City":"' in item:
                        typ = "Simon Mall"
                        website = "simon.com"
                        lat = item.split('"Latitude":')[1].split(",")[0]
                        lng = item.split('"Longitude":')[1].split(",")[0]
                        loc = (
                            "https://www.simon.com/mall/"
                            + item.split('"MallShortName":"')[1].split('"')[0]
                        )
                        hours = ""
                        r2 = session.get(loc, headers=headers)
                        for line2 in r2.iter_lines():
                            if '"HoursOutlook":{"' in line2:
                                days = line2.split('StartDaysOfWeekAbbreviation":"')
                                for day in days:
                                    if '"HoursOutlook"' not in day:
                                        hrs = (
                                            day.split('"')[0]
                                            + "-"
                                            + day.split('EndDaysOfWeekAbbreviation":"')[
                                                1
                                            ].split('"')[0]
                                            + ": "
                                        )
                                        hrs = (
                                            hrs
                                            + day.split('"OpenTimeDescription":"')[
                                                1
                                            ].split('"')[0]
                                            + "-"
                                            + day.split('"CloseTimeDescription":"')[
                                                1
                                            ].split('"')[0]
                                        )
                                        if hours == "":
                                            hours = hrs
                                        else:
                                            hours = hours + "; " + hrs
                                hours = hours.replace("Sun-Sun", "Sun")
                                hours = hours.replace("Sat-Sat", "Sat")
                                hours = hours.replace("Fri-Fri", "Fri")
                                if hours.count(";") == 3:
                                    hours = hours.rsplit(";", 1)[0].strip()
                        store = item.split('"Id":')[1].split(",")[0]
                        country = item.split('"CountryName":"')[1].split('"')[0]
                        if country == "CANADA":
                            country = "CA"
                        if country == "UNITED STATES":
                            country = "US"
                        add = (
                            item.split('{"Address1":"')[1].split('"')[0]
                            + " "
                            + item.split('"Address2":"')[1].split('"')[0]
                        )
                        add = add.strip()
                        city = item.split('"City":"')[1].split('"')[0]
                        state = item.split('"StateCode":"')[1].split('"')[0]
                        zc = item.split('"Zip":"')[1].split('"')[0]
                        name = item.split('"DisplayName":"')[1].split('"')[0]
                        try:
                            phone = item.split('"PhoneNumber":{"Origin":"')[1].split(
                                '"'
                            )[0]
                        except:
                            phone = "<MISSING>"
                        if hours == "":
                            hours = "<MISSING>"
                        yield SgRecord(
                            locator_domain=website,
                            page_url=loc,
                            location_name=name,
                            street_address=add,
                            city=city,
                            state=state,
                            zip_postal=zc,
                            country_code=country,
                            phone=phone,
                            location_type=typ,
                            store_number=store,
                            latitude=lat,
                            longitude=lng,
                            hours_of_operation=hours,
                        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
