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
    url = "https://stoneyriver.com/locations/"
    r = session.get(url, headers=headers)
    lines = r.iter_lines()
    for line in lines:
        if 'Book Now <span class="screenreadable">' in line:
            name = line.split('Book Now <span class="screenreadable">')[1].split("<")[0]
            website = "stoneyriver.com"
            typ = name.split(" |")[0]
            country = "US"
            lat = "<MISSING>"
            lng = "<MISSING>"
            hours = ""
            store = line.split('{"venueId":')[1].split(",")[0]
        if "google.com/maps/" in line or "maps.google.com/" in line:
            if "/@" in line:
                lat = line.split("/@")[1].split(",")[0]
                lng = line.split("/@")[1].split(",")[1]
            else:
                try:
                    lat = line.split("sll=")[1].split(",")[0]
                    lng = line.split("sll=")[1].split(",")[1].split("&")[0]
                except:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
        if "<address>" in line:
            add = (
                line.split("<address>")[1]
                .split("</a></address><br />")[0]
                .split("<")[0]
            )
            city = (
                line.split("<address>")[1]
                .split("</a></address><br />")[0]
                .rsplit("<br />", 1)[1]
                .split(",")[0]
            )
            state = (
                line.split("<address>")[1]
                .split("</a></address><br />")[0]
                .rsplit("<br />", 1)[1]
                .split(",")[1]
                .rsplit(" ", 1)[0]
                .strip()
            )
            zc = (
                line.split("<address>")[1]
                .split("</a></address><br />")[0]
                .rsplit("<br />", 1)[1]
                .split(",")[1]
                .rsplit(" ", 1)[1]
                .strip()
            )
            zc = zc.replace("</address>", "")
            phone = line.split('<a href="tel:')[1].split('"')[0]
            g = next(lines)
            g = next(lines)
            while "pm<" in g or "pm," in g or "Daily<" in g:
                hrs = g.split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
                g = next(lines)
            hours = (
                hours.replace("; Dining Room Open", "")
                .replace("-->", "")
                .replace(",;", ";")
            )
            purl = "https://stoneyriver.com/locations/"
            hours = (
                hours.replace("&#8211;", "-").replace("<br/>", "").replace("<br />", "")
            )
            if "phone." in hours:
                hours = hours.split("phone.")[1].strip()
            if "Annapolis" in city:
                lat = "38.99067"
                lng = "-76.546898"
            if hours == "":
                hours = "<MISSING>"
            if "Oak Brook" in city:
                hours = "Sun-Thurs: 11:30am-9pm; Fri-Sat: 11:30am-10pm"
            if "; Outdoor" in hours:
                hours = hours.split("; Outdoor")[0].strip()
            if "; Patio" in hours:
                hours = hours.split("; Patio")[0].strip()
            if "; Dine" in hours:
                hours = hours.split("; Dine")[0].strip()
            if "3900 Sum" in add:
                hours = hours.replace("; Mon", "Mon")
            if "Northbrook" in name:
                hours = "Mon-Thurs 11am-9pm; Fri 11am-10pm; Sat 11:30am-10pm; Sun 11:30am-9pm"
            if "Annapolis" in name:
                hours = "Sun-Thurs 11:30am-9pm; Fri-Sat 11:30am-10pm"
            if "Livonia" in name:
                hours = "Sun 11:30am-9pm; Mon-Thurs 11am-9pm; Mon-Thurs 11am-9pm"
            if "102 Oxmoor Ct" in add:
                hours = "Sun-Thurs 11am-9pm; Fri-Sat 11am-10pm"
            yield SgRecord(
                locator_domain=website,
                page_url=purl,
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
