from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup
import time
import csv
import re

logger = SgLogSetup().get_logger("mmfoodmarket_com")

session = SgRequests()

headers = {
    "authority": "mmfoodmarket.com",
    "method": "POST",
    "path": "/en/store-locator",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "content-length": "21814",
    "content-type": "application/x-www-form-urlencoded",
    "cookie": "_ga=GA1.2.697219837.1606368631; _gcl_au=1.1.1834758421.1606368632; rsci_vid=a6fbebc1-ab32-a61e-1b9c-b4063939b573; ASP.NET_SessionId=2bkbtd5gmhfqzzp3vjyeizxj; shoppingCartId=e51c7188-ea5b-433f-85e0-a7bc7aacbc8c; _fbp=fb.1.1606368634742.1768075909; _ce.s=v11.rlc~1608173317674~v~27d6fe4d069809676729688ae024c5ba8586d45c~vv~3~ir~1~nvisits_null~1~validSession_null~1; _gid=GA1.2.1567851707.1613718028; _hjid=12e12c6a-d432-47a8-b3ff-7831ccacb5de; _hjFirstSeen=1; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; ABTasty=uid=187hjedcyn91326y&fst=1606847489236&pst=1609764046719&cst=1613718023537&ns=20&pvt=72&pvis=72&th=; ABTastySession=mrasn=&lp=https%253A%252F%252Fmmfoodmarket.com%252F&sen=2; __atuvc=12%7C48%2C2%7C49%2C11%7C50%2C1%7C51%2C3%7C7; __atuvs=602f6208edcc15fc002; _uetsid=265afe40728011eb868c9d7dfe5c0769; _uetvid=265b9f60728011eb9732b5964d374e87",
    "origin": "https://mmfoodmarket.com",
    "referer": "https://mmfoodmarket.com/en/store-locator",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

header1 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    pattern = re.compile(r"\s\s+")
    data = []
    hrs = ""
    url = "https://mmfoodmarket.com/en/store-locator"
    state_list = [
        "AB",
        "BC",
        "MB",
        "NB",
        "NL",
        "NW",
        "NS",
        "ON",
        "PE",
        "QC",
        "SK",
        "YT",
    ]
    for state in state_list:
        formdata1 = {
            "ctl25_TSSM": ";Telerik.Sitefinity.Resources, Version=12.2.7232.0, Culture=neutral, PublicKeyToken=b28c218413bdf563:en:4ce39564-eafe-4a26-9ef6-244a21c7a8bb:7a90d6a:83fa35c7;Telerik.Web.UI, Version=2019.3.917.45, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en:cb7ecd12-8232-4d4a-979d-f12706320867:580b2269:eb8d8a8e",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": "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",
            "__VIEWSTATEGENERATOR": "6E96F86F",
            "__EVENTVALIDATION": "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",
            "fakeusernameremembered": "",
            "fakepasswordremembered": "",
            "ctl00$Topheader$T26E5E929115$txt_productSearch": "",
            "ctl00_CustomBreadcrumbs_ctl00_ctl00_Breadcrumb_ClientState": "",
            "ctl00$ProductsSearch$T26E5E929063$txt_productSearch": "",
            "ctl00$content$C002$hdnLat": "",
            "ctl00$content$C002$hdnLong": "",
            "ctl00$content$C002$txtPostalCode": "",
            "ctl00$content$C002$drpProvince": "AB",
            "ctl00$content$C002$drpCity": "0",
            "ctl00$content$C002$btnPFSubmit": "Submit",
        }
        r = session.post(url, data=formdata1, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "store_detail"})
        datalist = loclist.findAll("div", {"class": "data"})
        for dataa in datalist:
            link = dataa.find("a")
            link = link["href"]
            store = "https://mmfoodmarket.com/en/" + link
            p = session.get(store, headers=header1)
            soup = BeautifulSoup(p.text, "html.parser")
            locdata = soup.find("div", {"id": "content_C006_Col00"})
            title = locdata.find("h1").text
            title = title.lstrip()
            title = title.rstrip()
            address = locdata.find("p")
            address = address.get_text(strip=True, separator="|").strip()
            address = re.sub(pattern, "\n", address).split("\n")
            if len(address) == 3:
                streetncity = address[0]
                state = address[1]
                codenphone = address[2]
            if len(address) == 5:
                streetncity = address[0] + " " + address[1] + " " + address[2]
                state = address[3]
                codenphone = address[4]
            if len(address) == 4:
                streetncity = address[0] + " " + address[1]
                state = address[2]
                codenphone = address[3]
            streetncity = streetncity.split("|")
            city = ""
            street = ""

            if len(streetncity) == 2:
                street = streetncity[0]
                city = streetncity[1]
            if len(streetncity) == 3:
                street = streetncity[0] + " " + streetncity[1]
                city = streetncity[2]
            city = city.rstrip(",")

            codenphone = codenphone.split("|")
            pcode = codenphone[0]
            phone = codenphone[1]

            hours = locdata.findAll("li")
            for days in hours:
                day = days.find("span", {"class": "store-hours-title"}).text
                hrstime = days.find("span", {"class": "store-hours-time"}).text
                time = day + " " + hrstime
                hrs = hrs + time + ", "
            HOO = hrs.rstrip(", ")
            hrs = ""
            storeid = store.lstrip("https://mmfoodmarket.com/en/grocery-stores/")
            storeid = storeid.split("/")[1]

            scr = locdata.findAll("script")
            scr = scr[1]
            scr = str(scr)
            scr = scr.split('"latitude": ')[1].split("},")[0]
            lat = scr.split(",")[0].strip()
            longt = scr.split('"longitude": ')[1].strip()

            data.append(
                [
                    "https://mmfoodmarket.com/en/store-locator",
                    store,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "CAN",
                    storeid,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    HOO,
                ]
            )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
