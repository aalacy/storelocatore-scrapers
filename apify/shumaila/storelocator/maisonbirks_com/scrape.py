import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_data():

    url = "https://www.maisonbirks.com/en/store/locator/ajaxlist/"
    province = {
        "Alberta": "AB",
        "British Columbia": "BC",
        "Manitoba": "MB",
        "New Brunswick": "NB",
        "Newfoundland and Labrador": "NL",
        "Northwest Territories": "NT",
        "Nova Scotia": "NS",
        "Nunavut": "NU",
        "Ontario": "ON",
        "Prince Edward Island": "PE",
        "Quebec": "QC",
        "Saskatchewan": "SK",
        "Yukon": "YT",
        "Florida": "FL",
        "Albama": "AL",
        "Alabama": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "District of Columbia": "DC",
    }

    r = session.get(url, headers=headers)
    r = r.text.split(":", 1)[1].split(',"is_last_page')[0]

    r = json.loads(r)

    for store in r:

        try:

            ltype = store["additional_attributes"]["type"]["label"]
        except:

            ltype = store["additional_attributes"]["brands"]["label"]
        storeid = "<MISSING>"
        title = store["name"]

        ccode = store["country_id"]

        city = store["city"]
        pcode = store["postcode"]
        try:
            state = store["region"]

            state = province[state]
        except:
            state = "<MISSING>"
        street = store["address"][0]
        if "Beaver Creek Plaza" not in street:
            street = street.split(city)[0].replace(",", "")
        link = store["additional_attributes"]["url_key"]
        lat = store["latitude"]
        longt = store["longitude"]
        phone = store["telephone"]
        hourd = store["opening_hours"]
        hourd = json.loads(hourd)

        hours = ""
        for hr in hourd:
            opend = hr["open_formatted"]
            closed = hr["close_formatted"]
            if len(opend) < 2:
                opend = "Closed"
            else:
                opend = opend + " - " + closed
            hours = hours + hr["dayLabel"] + " : " + opend + " "
        yield SgRecord(
            locator_domain="https://www.maisonbirks.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(storeid),
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
