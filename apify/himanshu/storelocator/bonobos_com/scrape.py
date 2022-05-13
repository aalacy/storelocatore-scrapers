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
    "cookie": "ConstructorioID_client_id=36be3da1-5827-43bc-8ee6-d38e6e31ffde; _pxvid=f0569bd5-c16a-11ec-9f2b-477859734273; optimizely_NewCustomerPopupModal=%7B%22visits%22:2%7D; ajs_anonymous_id=%222579a07c-2441-4cfc-b185-c69774622cba%22; _gcl_au=1.1.1158360164.1650542568; _fbp=fb.1.1650542571087.331565872; __attentive_cco=1650542572891; __attentive_id=3cd2723392064e93868f63174d96c911; _attn_=eyJ1Ijoie1wiY29cIjoxNjUwNTQyNTcyOTExLFwidW9cIjoxNjUwNTQyNTcyOTExLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjNjZDI3MjMzOTIwNjRlOTM4NjhmNjMxNzRkOTZjOTExXCJ9In0=; _hjSessionUser_42288=eyJpZCI6IjA1ZWI0MWY3LTdmODQtNWFjZi04OTRhLTk3OWY1ZWUyY2JkYSIsImNyZWF0ZWQiOjE2NTA1NDI1NjEwNTEsImV4aXN0aW5nIjp0cnVlfQ==; __qca=P0-271932049-1650542580511; _hjSession_42288=eyJpZCI6ImZhZjgzNzg4LTM0NjYtNDliNC1iNzExLWFkNTkwNjI5NDk4OSIsImNyZWF0ZWQiOjE2NTIyMDQzODUxNjIsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; pxcts=2e4e2fbe-d088-11ec-935e-4e776466756a; _gid=GA1.2.1465203776.1652204387; FPC=26c3aa16-d7ad-47ab-8b2297bbfd3b1c80; IR_gbd=bonobos.com; _rdt_uuid=1652204387963.30d779aa-6bff-4895-9237-1b9c73c9ab6a; _clck=1o86b9k|1|f1c|0; _hjIncludedInPageviewSample=1; _hjIncludedInSessionSample=0; ABTasty=uid=vp9gwrqddmm9bj6m&fst=1650542558779&pst=1651012958361&cst=1652204385111&ns=5&pvt=34&pvis=9&th=809362.1005353.34.9.5.1.1650542561750.1652207862355.1_826736.1027185.25.4.4.1.1650542561764.1651013630259.1_840352.1045054.3.1.3.1.1650542561761.1651008317223.1; ABTastySession=mrasn=&sen=17&lp=https%253A%252F%252Fbonobos.com%252F; bonobos_session=%7B%22start%22:1652204384595,%22expiry%22:1652209662564%7D; _px3=f3f8e9a99e3ceaa23daf8ae3bcf753901b925d206e0667e9ad6a9ddee9f44f1b:7C3L4EAjTfJzzdjNdrm5gQhdNDUiQ9DiXdbFMnHGG7sRUZbToDRu9LjSIFwL2lF4I5MnCInlaiVA58u+4Pmyvw==:1000:qs0dQBaCcp/ojdjTeEMTsjKZPIPKPG2nLBOxMpnsKqvJozGe7J34prFD86A47MrMJDRuz36OXpjOgfIPKJqa8d152Wp1ppl1QEMchVFZ+9B3AToDhhXOKUVoRkbAQOzXmX6lhV69MfO3G7cIWte8uuw+Hq/ALtUXh9CH1HnU9EZPiIdkwpbboZquYvBr9CwwrdMjOjeShkYtjLahun4wNg==; _ga_VMBTKXPZXB=GS1.1.1652204387.6.1.1652207863.0; IR_11113=1652207864018%7C0%7C1652207864018%7C%7C; amplitude_id_3fee4ba39723e18212fe3c36d058b407bonobos.com=eyJkZXZpY2VJZCI6ImMxMGExNjg2LTAzMTQtNDVlZC05YWQ1LTM4M2VhNzJjMDE0YlIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTY1MjIwNDM4Nzc0MiwibGFzdEV2ZW50VGltZSI6MTY1MjIwNzg2NDAzNywiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6NjAsInNlcXVlbmNlTnVtYmVyIjo2MH0=; _ga=GA1.2.1586111773.1650542567; _uetsid=2f79bef0d08811eca4d9af9cc1563256; _uetvid=f6549fd0c16a11ecbd70db3af429f4cd; _clsk=1u40o89|1652207865580|9|1|e.clarity.ms/collect",
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
            street = street.lstrip().replace(",", "")
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
