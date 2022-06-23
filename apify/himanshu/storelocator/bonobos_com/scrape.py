from bs4 import BeautifulSoup
import re
import usaddress
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Cookie": "ConstructorioID_client_id=40716730-50e9-4ab6-8ac9-85752aa14306; bonobos_session=%7B%22start%22:1655840738750,%22expiry%22:1655842574555%7D; optimizely_NewCustomerPopupModal=%7B%22visits%22:1%7D; ABTasty=uid=6ha13k54bvk52xrx&fst=1655840739215&pst=-1&cst=1655840739215&ns=1&pvt=1&pvis=1&th=809362.1005353.1.1.1.1.1655840739435.1655840739435.1; ABTastySession=mrasn=&sen=1&lp=; pxcts=ba30f1e0-f19a-11ec-b319-65546b725751; _pxvid=ba30dc05-f19a-11ec-b319-65546b725751; _px3=47fc18fe3c217632ef7ea94b18aa25cea18bf68e90fd2cc2ee97db80e6f57f5b:5pS5oT04zLDGkiQHH1joBceaX4jgdyIB/lQpzRrzUX9iEwGKBqEoIAt9NkaIqDm3Wlprepok04lnslvGprPMlg==:1000:OqPAKD5Wptja2K4AYn/rx7fuJAvYF39MQuf/IEu7ArwModY8dAD8808vXxGjE6X7tqbIM7fjEueG9r73V/5/HKi3ERXEn3rp0xl8LjxJ3/qqTOv8romxgxlmLt0W4D5VFrKNEUsunkyqxws6WARvYl7uL9lTwzLF0jUZZdKjsbz8pDdkGYR7mTnw4h0Cq1f/CKlZmNPxMFTJun6k1eniuw==; _hjSessionUser_42288=eyJpZCI6Ijg4ODAwY2UyLTQwMTUtNTUxZC05NzQ2LTUwYTAzMDM2YTBiOSIsImNyZWF0ZWQiOjE2NTU4NDA3NDA0NjMsImV4aXN0aW5nIjpmYWxzZX0=; _hjFirstSeen=1; _hjIncludedInSessionSample=0; _hjSession_42288=eyJpZCI6IjMwYjIzNDZhLTJjNmMtNGJmYi04MWM1LTIyNGQxODZhMjdiNyIsImNyZWF0ZWQiOjE2NTU4NDA3NDA1MDMsImluU2FtcGxlIjpmYWxzZX0=; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=1; ajs_anonymous_id=%223c6e48b8-cc47-4177-8cbf-180380fc1e93%22; FPC=934bbe83-4ba8-4979-b3cd9557dafcb221; _gcl_au=1.1.1839311446.1655840743; _ga_VMBTKXPZXB=GS1.1.1655840742.1.0.1655840775.0; _ga=GA1.2.1885785808.1655840743; _rdt_uuid=1655840742957.064eca9c-b985-4090-b4f3-e585b083ecc3; IR_gbd=bonobos.com; IR_11113=1655840743107%7C0%7C1655840743107%7C%7C; _gid=GA1.2.1118755253.1655840744; amplitude_id_3fee4ba39723e18212fe3c36d058b407bonobos.com=eyJkZXZpY2VJZCI6ImViNzU3ZGZhLWFkZjUtNGVjOS05ZDI1LWMxNGEwYzkzMmViNFIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTY1NTg0MDc0MzgzNSwibGFzdEV2ZW50VGltZSI6MTY1NTg0MDc0MzgzNiwiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6MSwic2VxdWVuY2VOdW1iZXIiOjF9; _gat=1; _fbp=fb.1.1655840744482.918857653; __qca=P0-828986717-1655840744229; _clck=1cr6gxk|1|f2i|0; _clsk=1sfoz9a|1655840745326|1|1|m.clarity.ms/collect; _uetsid=bc323580f19a11ecb7da5384d9d0c020; _uetvid=bc3256e0f19a11ecbd67f9815f271def",
    "if-none-match": '"47939-Y+nE1nGPi0j+XtD/aIJ82Egb+5M"',
}


def fetch_data():
    session = SgRequests()
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    url = "https://bonobos.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=locations]")
    t = 0
    for link in linklist:

        link = link["href"]

        if "city-creek-center-salt-lake-city" in link:

            title = "City Creek Center, Salt Lake City"
            street = "50 South Main St"
            city = "Salt Lake City"
            state = "UT"
            pcode = "84101"
            phone = "(801) 363-2666"
            hours = "Sun: CLOSED Mon - Thu: 11:00 AM - 7:00 PM Fri - Sat: 11:00 AM - 8:00 PM"
            lat = "39.3090696"
            longt = "-111.4686535"
        else:
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            t = t + 1

            content = soup.find("div", {"class": "contentful-block-component"})
            content = re.sub(cleanr, "\n", str(content))
            content = re.sub(pattern, "\n", str(content)).replace("\xa0", " ").strip()
            title = content.splitlines()[0]
            address = (
                content.split(title, 1)[1]
                .split("(", 1)[0]
                .replace("Get Directions", "")
                .replace(", US", "")
                .replace(", Located on the 1st floor", "")
                .replace("Located at the corner of Court &amp; Dean St", "")
                .replace("\n", " ")
                .strip()
            )

            address = usaddress.parse(address)

            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    if temp[0] in city:
                        continue
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1
            street = (
                street.lstrip()
                .replace(",", "")
                .replace("; Parking validated in the Z Lot", "")
                .strip()
            )
            city = city.lstrip().replace(",", "")
            state = state.lstrip().replace(",", "")
            pcode = pcode.lstrip().replace(",", "")

            phone = content.split("(", 1)[1].split("\n", 1)[0]
            phone = "(" + phone
            hours = (
                content.split("Hours", 1)[1]
                .split("Book", 1)[0]
                .replace("\n", " ")
                .strip()
            )
            try:
                lat, longt = (
                    r.text.split("https://www.google.com/maps/", 1)[1]
                    .split("@", 1)[1]
                    .split("data", 1)[0]
                    .split(",", 1)
                )
                longt = longt.split(",", 1)[0]
            except:
                lat = longt = "<MISSING>"
            if ">" in lat:
                lat = longt = "<MISSING>"
            try:
                hours = hours.split(" Appointments", 1)[0]
            except:
                pass
            try:
                hours = hours.split("We are", 1)[0]
            except:
                pass
            try:
                hours = hours.split(" Parking ", 1)[0]
            except:
                pass
            try:
                street = street.split(" Located ", 1)[0]
            except:
                pass
            try:
                city = city.split(" Located ", 1)[0]
            except:
                pass
        yield SgRecord(
            locator_domain="https://bonobos.com/",
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
            hours_of_operation=hours.replace(": Sun", "Sun").strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
