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
    "content-length": "20388",
    "content-type": "application/x-www-form-urlencoded",
    "cookie": "_ga=GA1.2.697219837.1606368631; _gcl_au=1.1.1834758421.1606368632; rsci_vid=a6fbebc1-ab32-a61e-1b9c-b4063939b573; ASP.NET_SessionId=2bkbtd5gmhfqzzp3vjyeizxj; shoppingCartId=e51c7188-ea5b-433f-85e0-a7bc7aacbc8c; _fbp=fb.1.1606368634742.1768075909; __atuvc=12%7C48%2C2%7C49%2C11%7C50%2C1%7C51; _ce.s=v11.rlc~1608173317674~v~27d6fe4d069809676729688ae024c5ba8586d45c~vv~3~ir~1~nvisits_null~1~validSession_null~1; _gid=GA1.2.2095504239.1609057213; _uetsid=578fd2f0481c11eb9365c734dfa6a58a; _uetvid=80aedb402fa811eb8f272b4c3d83b145; ABTasty=uid=187hjedcyn91326y&fst=1606847489236&pst=1608919880660&cst=1609057213208&ns=7&pvt=18&pvis=18&th=",
    "origin": "https://mmfoodmarket.com",
    "referer": "https://mmfoodmarket.com/en/store-locator",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
            "ctl00$ScriptManager": "ctl00$content$C002$UpdatePanel1|ctl00$content$C002$drpProvince",
            "ctl25_TSSM": ";Telerik.Sitefinity.Resources, Version=12.0.7000.0, Culture=neutral, PublicKeyToken=b28c218413bdf563:en:49f0c3aa-73da-4308-80bd-c9555648caff:7a90d6a:83fa35c7;Telerik.Web.UI, Version=2019.1.115.45, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en:9158ae02-bc1e-43e0-912e-ac8b68761b62:580b2269:eb8d8a8e",
            "__EVENTTARGET": "ctl00$content$C002$drpProvince",
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
            "ctl00$content$C002$drpProvince": state,
            "ctl00$content$C002$drpCity": "-1",
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
