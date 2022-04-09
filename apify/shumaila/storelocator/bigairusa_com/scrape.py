from bs4 import BeautifulSoup
import re
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

    pattern = re.compile(r"\s\s+")
    url = "https://www.bigairusa.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("section", {"data-id": "3d481e14"}).findAll("a")
    for link in linklist:
        link = link["href"]
        if ("http") in link:
            continue
        else:
            link = "https://www.bigairusa.com" + link
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.find("ul", {"class": "elementor-icon-list-items"})
        title = content.find("a").text
        phone = content.findAll("span")[-1].text
        hours = ""
        try:
            hourslist = (
                "Monday "
                + soup.select_one('section:contains("Monday")')
                .text.split("Monday", 1)[1]
                .split("Info", 1)[0]
            )

            hourslist = re.sub(pattern, "\n", str(hourslist))

            hourslist = hourslist.splitlines()
            flag = 0
            for hr in hourslist:

                if "toddler" in hr.lower() or "cosmic" in hr.lower():

                    if "am" not in hr.lower() and "pm" not in hr or "toddler" in hr:
                        flag = 1
                    else:
                        flag = 0

                        if ("General" not in hr) or ("Madness" not in hr):

                            try:
                                hr = hr.split("General", 1)[0]
                                hours = hours + hr + " "
                            except:
                                pass
                            continue
                        else:

                            if "Madness" in hr:

                                hr = hr.split("Madness", 1)[1].split("Genera", 1)[0]
                                hours = hours + hr + " "
                            else:

                                hr = hr.split("Genera", 1)[0].strip()
                                hours = hours + hr + " "
                else:
                    if flag == 1:
                        flag = 0
                        continue
                    else:

                        hours = hours + hr + " "
        except:

            hrlink = link + "hours/"

            r2 = session.get(hrlink, headers=headers)
            soup2 = BeautifulSoup(r2.text, "html.parser")
            hourslist = (
                "MONDAY " + soup2.text.split("MONDAY", 1)[1].split("Holidays", 1)[0]
            )
            hourslist = re.sub(pattern, "\n", str(hourslist)).splitlines()
            flag = 0

            for hr in hourslist:

                if (
                    ("day" in hr.lower() and "-" not in hr)
                    or ("closed" in hr.lower())
                    or ("General" in hr)
                    or (
                        ("pm" in hr.lower() and "-" in hr)
                        and ":" not in hr
                        and "General" not in hr
                    )
                ):

                    try:
                        hr = hr.split("Cosmic", 1)[0]
                    except:
                        pass
                    try:
                        hr = hr.lower().split("toddler", 1)[0]
                    except:
                        pass
                    try:
                        hr = hr.lower().split(":", 1)[1].strip()
                    except:
                        pass
                    hours = hours + hr + " "
        hours = (
            hours.replace("General Admission ", "")
            .replace("*", "")
            .replace("Calendar", "")
            .replace("day", "day ")
            .strip()
        )
        try:
            hours = hours.split("Calendar", 1)[0]
        except:
            pass
        try:

            try:
                addrlink = soup.select('a:contains("Directions")')[0]["href"]
            except:
                addrlink = soup.select_one("a[href*=map]")["href"]
            lat = longt = "<MISSING>"
            if "map" in addrlink:

                lat, longt = addrlink.split("@", 1)[1].split("data", 1)[0].split(",", 1)
                longt = longt.split(",", 1)[0]
                addrlink = soup.select('a:contains("Directions")')[1]["href"]
            else:

                try:
                    lat, longt = (
                        soup.select_one("a[href*=map]")["href"]
                        .split("@", 1)[1]
                        .split("data", 1)[0]
                        .split(",", 1)
                    )
                    longt = longt.split(",", 1)[0]
                except:
                    pass
            r3 = session.get(addrlink, headers=headers)
            soup3 = BeautifulSoup(r3.text, "html.parser")

            try:

                address = soup3.find("h5", {"class": "elementor-heading-title"}).text

                try:
                    street, city, state = address.split("located ", 1)[1].split(", ")

                    state, pcode = state.split(" ", 1)
                except:
                    try:
                        street, city = address.split("Directions | ", 1)[1].split(
                            "  |  ", 1
                        )
                        city, state = city.split(", ", 1)
                        state, pcode = state.split(" ", 1)
                    except:
                        street, city, state = address.split("Address:", 1)[1].split(
                            ", "
                        )

                        state, pcode = state.split(" ", 1)
                        pcode.split("\n", 1)[0]
            except:

                addrlink = soup3.select_one("iframe[src*=embed]")["src"]

                r = session.get(addrlink, headers=headers)

                try:
                    street, city, state = (
                        r.text.split('"Building","')[1].split('"', 1)[0].split(", ")
                    )

                    state, pcode = state.split(" ", 1)
                except:
                    street, city, state = (
                        r.text.split('center","')[1].split('"', 1)[0].split(", ")
                    )

                    state, pcode = state.split(" ", 1)
        except:

            lat, longt = (
                soup.select_one("a[href*=map]")["href"]
                .split("@", 1)[1]
                .split("data", 1)[0]
                .split(",", 1)
            )
            longt = longt.split(",", 1)[0]
            city, state = soup.select_one("a[href*=map]").text.split(", ")
            street = pcode = "<MISSING>"
        if "Greenville" in city:
            street = "36 Park Woodruff Dr"
            pcode = "29607"
        hours = hours.replace(" (Toddler time: 10:00 AM to 1:00 PM) ", "").replace(
            " (Toddler time: 9 AM to 11 AM)", ""
        )
        try:
            hours = hours.split(" Tuesday s and Thursday s ", 1)[0]
        except:
            pass
        if "https://www.bigairusa.com/corona/" in link:
            hours = hours.replace(
                "Friday 3:00 PM to 7:00 PM 11:00 AM to 7:00 PM 11:00 AM to 8:00 PM",
                "Friday  3:00 PM to 7:00 PM Saturday 11:00 AM to 7:00 PM Sunday 11:00 AM to 8:00 PM",
            )
        if "https://www.bigairusa.com/buena-park/" in link:
            hours = hours.replace("Toddler Time: 10:00 AM to 1:00 PM", "")
        yield SgRecord(
            locator_domain="https://www.bigairusa.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
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
