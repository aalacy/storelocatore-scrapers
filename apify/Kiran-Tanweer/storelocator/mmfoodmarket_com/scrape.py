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
            "fakeusernameremembered": "",
            "fakepasswordremembered": "",
            "ctl00$Topheader$T26E5E929115$txt_productSearch": "",
            "ctl00_CustomBreadcrumbs_ctl00_ctl00_Breadcrumb_ClientState": "",
            "ctl00$ProductsSearch$T26E5E929063$txt_productSearch": "",
            "ctl00$content$C002$hdnLat": "",
            "ctl00$content$C002$hdnLong": "",
            "ctl00$content$C002$txtPostalCode": "",
            "ctl00$content$C002$drpProvince": state,
            "ctl00$content$C002$drpCity": "0",
            "ctl00$content$C002$btnPFSubmit": "Submit",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": "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",
            "__VIEWSTATEGENERATOR": "6E96F86F",
            "__EVENTVALIDATION": "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",
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
