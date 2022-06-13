from bs4 import BeautifulSoup
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
    "Cookie": "_gcl_au=1.1.492775561.1649979093; _ga=GA1.2.1102456833.1649979093; _fbp=fb.1.1649979094512.31143188; city=Hohenwald; hospital_id=6936; hospital_name=Hohenwald; hospital_post_id=3486; isLocationSet=yes; region_name=Tennessee; thid=5105; _gid=GA1.2.633866335.1650293362; PHPSESSID=0f22f661b8d25dfcdec92b110d5827f4; cebs=1; lat=36.1972824; lng=-85.4169211; _yfpc=803487941266; _gat_UA-47751755-1=1; _ce.s=v~6b2f32df052689e4a6317c1f1b62796f8b06b899~vpv~2~v11.rlc~1650317400429~ir~1~gtrk.la~l258ldk5",
}


def fetch_data():

    url = "https://fastpacehealth.com/wp-admin/admin-ajax.php"
    dataobj = {
        "action": "load_more_dealers",
        "address": "",
        "lat": "36.1972824",
        "lng": "-85.4169211",
        "radius": "10000",
        "post_length": "0",
    }

    loclist = session.post(url, headers=headers, data=dataobj).json()["location_list"]
    loclist = BeautifulSoup(loclist.replace("\\", ""), "html.parser").findAll(
        "li", {"class": "single-item"}
    )
    for loc in loclist:

        store = loc["id"].replace("li_store_id_", "")
        title = loc["data-hname"]
        try:
            facility = str(loc).split('data-yext-id="Facility-', 1)[1].split('"', 1)[0]
            loclink = (
                "https://knowledgetags.yextpages.net/embed?key=BW5iO01rVpuBJkLSsAXT5nv2m1ByWv-EEO_3Vgyk5k4Yx-lOn5kZUuXnfKQWh_8B&account_id=950683801497861850&entity_id=Facility-"
                + str(facility)
                + "&locale=en&v=20210504"
            )

            r = session.get(loclink, headers=headers).text
            link = r.split('"websiteUrl.url":"', 1)[1].split("?", 1)[0]
            address = r.split('"address":', 1)[1].split("}", 1)[0]
            address = address + "}"
            address = json.loads(address)
            city = address["addressLocality"]
            state = address["addressRegion"]
            pcode = address["postalCode"]
            street = address["streetAddress"]
            lat = r.split('"latitude":', 1)[1].split(",", 1)[0]
            longt = r.split('"longitude":', 1)[1].split("}", 1)[0]
            phone = r.split('"phone":"', 1)[1].split('"', 1)[0]
            hourslist = r.split('"openingHoursSpecification":', 1)[1].split("]", 1)[0]
            hourslist = hourslist + "]"
            hourslist = json.loads(hourslist)

            hours = ""
            for hr in hourslist:

                try:
                    day = hr["dayOfWeek"]
                    closestr = hr["closes"]
                    close = int(closestr.split(":", 1)[0])
                    if close > 12:
                        close = close - 12
                    openstr = hr["opens"]
                    check = int(openstr.split(":", 1)[0])
                    if check > 12:
                        check = check - 12
                        hours = (
                            hours
                            + day
                            + " "
                            + str(check)
                            + ":"
                            + openstr.split(":", 1)[1]
                            + " pm - "
                            + str(close)
                            + ":"
                            + closestr.split(":", 1)[1]
                            + " pm "
                        )
                    else:
                        hours = (
                            hours
                            + day
                            + " "
                            + openstr
                            + " am - "
                            + str(close)
                            + ":"
                            + closestr.split(":", 1)[1]
                            + " pm "
                        )
                except:
                    hours = hours + day + " Closed "
        except:

            hours = link = "<MISSING>"
            datanow = {"action": "load_single_clinic_page", "post_id": str(store)}
            locnow = session.post(url, headers=headers, data=datanow).json()[
                "location_markers"
            ][0]
            lat = locnow["lat"]
            longt = locnow["lng"]
            link = (
                "https://fastpacehealth.com/location/"
                + str(loc).split("/location/", 1)[1].split("'", 1)[0]
            )
            address = str(loc).split("<p>", 1)[1].split("</p>", 1)[0]
            street, city = address.split("<br/>", 1)
            city, state = city.split(", ", 1)
            state, pcode = state.split(" ", 1)
            phone = (
                str(loc).split('<a href="tel:', 1)[1].split(">", 1)[1].split("<", 1)[0]
            )
        yield SgRecord(
            locator_domain="https://fastpacehealth.com/",
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
