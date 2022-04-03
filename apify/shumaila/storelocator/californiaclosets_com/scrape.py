from bs4 import BeautifulSoup
import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.californiaclosets.com/showrooms/"
    r = session.get(url, headers=headers)
    loclist = r.text.split('<script type="application/ld+json">')[1:]
    for loc in loclist:
        loc = loc.split("</script>", 1)[0]
        loc = json.loads(loc)
        title = loc["name"]
        link = loc["url"]
        phone = loc["telephone"]
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        try:
            ccode = loc["address"]["addressCountry"]
        except:
            if pcode.strip().isdigit():
                ccode = "US"
            else:
                ccode = "CA"
        ltype = loc["image"]
        if len(phone) < 3:
            ltype = "Coming Soon"
        else:
            ltype = "<MISSING>"
        lat = longt = hours = "<MISSING>"
        try:
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            if len(pcode) < 3:
                try:
                    pcode = (
                        r.text.split('"streetAddress":"' + street, 1)[1]
                        .split('"postalCode":"', 1)[1]
                        .split('"', 1)[0]
                        .strip()
                    )
                except:
                    try:
                        pcode = (
                            r.text.split('"postalCode":"', 1)[1]
                            .split('"', 1)[0]
                            .strip()
                        )
                    except:
                        pcode = soup.find(
                            "span", {"class": "c-address-postal-code"}
                        ).text
            try:
                lat = r.text.split('"latitude":', 1)[1].split(",", 1)[0]
                longt = r.text.split('"longitude":', 1)[1].split("}", 1)[0]
            except:
                try:
                    lat = r.text.split('latitude" content="', 1)[1].split('"', 1)[0]
                    longt = r.text.split('longitude" content="', 1)[1].split('"', 1)[0]
                except:
                    lat = longt = "<MISSING>"
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                try:
                    hours = (
                        soup.find("table", {"class": "hours"})
                        .text.replace("Day of the WeekHours", "")
                        .replace("PM", "PM ")
                        .replace("day", "day ")
                        .replace("losed", "losed ")
                        .strip()
                    )
                except:

                    hours = (
                        soup.find("div", {"class": "hours"})
                        .text.replace("SHOWROOM HOURS", "")
                        .replace("\n", " ")
                        .strip()
                    )
                    try:
                        hours = hours.split("Mon", 1)[1]
                        hours = "Mon" + hours
                    except:
                        pass
                    try:
                        hours = hours.split("More", 1)[0]
                    except:
                        pass
            except:
                hours = "<MISSING>"
            try:
                if "Canada" in ccode:
                    ccode = "CA"
                elif "USA" in ccode:
                    ccode = "US"
                elif "Mexico" in ccode or "Santiago" in ccode or "Garcia" in ccode:
                    ccode = "MX"
                elif "Domingo" in ccode:
                    ccode = "DO"
                elif "San Juan" in ccode:
                    ccode = "PR"
                else:
                    if pcode.isdigit():
                        ccode = "US"
                    elif len(pcode) > 5:
                        ccode = "CA"
                    else:
                        ccode = soup.find("span", {"itemprop": "addressCountry"}).text
            except:
                try:
                    ccode = (
                        r.text.split('"streetAddress":"' + street, 1)[1]
                        .split('"addressCountry":"', 1)[1]
                        .split('"', 1)[0]
                    )
                except:
                    try:
                        ccode = soup.find("span", {"itemprop": "addressCountry"}).text
                    except:
                        if pcode.strip().isdigit():
                            ccode = "US"
                        else:
                            ccode = "CA"
            if "Canada" in ccode:
                ccode = "CA"
            try:
                phone = phone.split("<", 1)[0]
            except:
                pass
            if "22000 Willamette Dr" in street:
                street = street + " Suite 103"
            try:
                hours = hours.split("MORE", 1)[0]
            except:
                pass
        except:
            pass
        yield SgRecord(
            locator_domain="https://www.californiaclosets.com/",
            page_url=link,
            location_name=title.replace("&#8211;", "-").strip(),
            street_address=street.replace(" </br>", "")
            .replace("<br>", " ")
            .replace("<br/>", " ")
            .strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=ltype,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
