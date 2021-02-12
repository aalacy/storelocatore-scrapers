from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("cloverdalepaint_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

cookies = {
    0: "ASP.NET_SessionId=bqcqiaudc0t5gqwizero1bec; _ga=GA1.2.1171242845.1610474373; _pin_unauth=dWlkPU5XWmtNVFV3TVdVdE5USmpaUzAwTWpVd0xUZ3lNVFF0T1dVNE9EVTBNalUwTjJReQ; _fbp=fb.1.1610474378230.488821239; _gid=GA1.2.1443751466.1610650057; _derived_epik=dj0yJnU9YU1TeHA4aUlrN3ZaeGY4alFGYTV2dTN2ZVVfM21kTW0mbj1MdWZLMi1JdmR4ZDlVSS1DdW5yMThnJm09MSZ0PUFBQUFBR0FBdWdVJnJtPTEmcnQ9QUFBQUFHQUF1Z1U",
    1: "ASP.NET_SessionId=bqcqiaudc0t5gqwizero1bec; _ga=GA1.2.1171242845.1610474373; _pin_unauth=dWlkPU5XWmtNVFV3TVdVdE5USmpaUzAwTWpVd0xUZ3lNVFF0T1dVNE9EVTBNalUwTjJReQ; _fbp=fb.1.1610474378230.488821239; _gid=GA1.2.1443751466.1610650057; _gat=1; _derived_epik=dj0yJnU9ZTl4bE1iZzEyS1BnREVTaGx6RFN1QlRhZ25aNFkyREEmbj05eHhTNFVVWHZCc2lWMDM2T3hGY2NBJm09MSZ0PUFBQUFBR0FBeVlNJnJtPTEmcnQ9QUFBQUFHQUF5WU0",
    2: "ASP.NET_SessionId=bqcqiaudc0t5gqwizero1bec; _ga=GA1.2.1171242845.1610474373; _pin_unauth=dWlkPU5XWmtNVFV3TVdVdE5USmpaUzAwTWpVd0xUZ3lNVFF0T1dVNE9EVTBNalUwTjJReQ; _fbp=fb.1.1610474378230.488821239; _gid=GA1.2.1443751466.1610650057; _gat=1; _derived_epik=dj0yJnU9dHU5bGdIcTJvWnV5a1dVM2VCT241OWVJeDl2bk16U1Qmbj1pSUxyTDNaS0hFcHhvbS12cUJRVU5BJm09MSZ0PUFBQUFBR0FBeXFnJnJtPTEmcnQ9QUFBQUFHQUF5cWc",
    3: "ASP.NET_SessionId=bqcqiaudc0t5gqwizero1bec; _ga=GA1.2.1171242845.1610474373; _pin_unauth=dWlkPU5XWmtNVFV3TVdVdE5USmpaUzAwTWpVd0xUZ3lNVFF0T1dVNE9EVTBNalUwTjJReQ; _fbp=fb.1.1610474378230.488821239; _gid=GA1.2.1443751466.1610650057; _derived_epik=dj0yJnU9MUhTR19nV0F5YWJ6NTUzSjRHVjJDR29tR19lRmF3QnUmbj1rQXlreVp2c19YNkE0NUZvcGhTQlp3Jm09MSZ0PUFBQUFBR0FBeXRvJnJtPTEmcnQ9QUFBQUFHQUF5dG8",
    4: "ASP.NET_SessionId=bqcqiaudc0t5gqwizero1bec; _ga=GA1.2.1171242845.1610474373; _pin_unauth=dWlkPU5XWmtNVFV3TVdVdE5USmpaUzAwTWpVd0xUZ3lNVFF0T1dVNE9EVTBNalUwTjJReQ; _fbp=fb.1.1610474378230.488821239; _gid=GA1.2.1443751466.1610650057; _gat=1; _derived_epik=dj0yJnU9anlBLUlfek9XSWVUeVozSEV0azlDblRJT3dSSXEzOUwmbj1MaVJ2MzEtcnlNaEdkUlRueHlnd2pRJm09MSZ0PUFBQUFBR0FBeTB3JnJtPTEmcnQ9QUFBQUFHQUF5MHc",
    5: "ASP.NET_SessionId=bqcqiaudc0t5gqwizero1bec; _ga=GA1.2.1171242845.1610474373; _pin_unauth=dWlkPU5XWmtNVFV3TVdVdE5USmpaUzAwTWpVd0xUZ3lNVFF0T1dVNE9EVTBNalUwTjJReQ; _fbp=fb.1.1610474378230.488821239; _gid=GA1.2.1443751466.1610650057; _derived_epik=dj0yJnU9RTJCZ2E1Wi1LeFdXdjV1eWItR2tuQTQtQTV4WF8zYVAmbj1oVlNRcE1ydFlSd1dlOEpWRzN4Q2NnJm09MSZ0PUFBQUFBR0FBeTRnJnJtPTEmcnQ9QUFBQUFHQUF5NGc",
    6: "ASP.NET_SessionId=bqcqiaudc0t5gqwizero1bec; _ga=GA1.2.1171242845.1610474373; _pin_unauth=dWlkPU5XWmtNVFV3TVdVdE5USmpaUzAwTWpVd0xUZ3lNVFF0T1dVNE9EVTBNalUwTjJReQ; _fbp=fb.1.1610474378230.488821239; _gid=GA1.2.1443751466.1610650057; _gat=1; _derived_epik=dj0yJnU9ZUlhcFJxeEJScmVodWJ4VFdfZnFNTXBUXzZtVXU4MXMmbj1ubDVoenNmTWhDclo1cGJQZklWLUFnJm09MSZ0PUFBQUFBR0FBeTZ3JnJtPTEmcnQ9QUFBQUFHQUF5Nnc",
    7: "ASP.NET_SessionId=bqcqiaudc0t5gqwizero1bec; _ga=GA1.2.1171242845.1610474373; _pin_unauth=dWlkPU5XWmtNVFV3TVdVdE5USmpaUzAwTWpVd0xUZ3lNVFF0T1dVNE9EVTBNalUwTjJReQ; _fbp=fb.1.1610474378230.488821239; _gid=GA1.2.1443751466.1610650057; _gat=1; _derived_epik=dj0yJnU9blQzVDVWSWlUbkZSYldpMjZhNjgzX3U2QzRiQVVTajEmbj15eUlkMVdla2JSQlJfb2VpSVlqb093Jm09MSZ0PUFBQUFBR0FBeTlNJnJtPTEmcnQ9QUFBQUFHQUF5OU0",
    8: "ASP.NET_SessionId=bqcqiaudc0t5gqwizero1bec; _ga=GA1.2.1171242845.1610474373; _pin_unauth=dWlkPU5XWmtNVFV3TVdVdE5USmpaUzAwTWpVd0xUZ3lNVFF0T1dVNE9EVTBNalUwTjJReQ; _fbp=fb.1.1610474378230.488821239; _gid=GA1.2.1443751466.1610650057; _derived_epik=dj0yJnU9VS1uMTlHQ0F5QjdnaGo3S05TWVRPaWNRSGJPc0k1clgmbj1kZ0ltSkRJMGRyRm9iNVU0SmhFR3pBJm09MSZ0PUFBQUFBR0FBekFFJnJtPTEmcnQ9QUFBQUFHQUF6QUU",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    i = 0
    j = 0
    url = "https://www.cloverdalepaint.com/store-locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("ul", {"class": "nav L4 active"}).findAll("li")
    for link in linklist:
        page = link.find("a")["href"]
        pagelink = "https://www.cloverdalepaint.com" + page
        headers2 = {
            "authority": "www.cloverdalepaint.com",
            "method": "GET",
            "path": page,
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "cookie": cookies[j],
            "referer": "https://www.cloverdalepaint.com/store-locations",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        }

        p = session.get(pagelink, headers=headers2, verify=False)
        soup = BeautifulSoup(p.text, "html.parser")
        information = soup.find("div", {"id": "map"}).findAll("script")
        info = information[1]
        info = str(info)
        info = info.lstrip("'")
        info = info.lstrip("<script>initialize(")
        info = info.lstrip("'")
        info = info.lstrip('<?xml version="1.0" encoding="utf-16"?>')
        info = info.lstrip("arkers>")
        info = info.lstrip()
        info = info.rstrip("')</script>")
        info = info.rstrip("</marke")
        info = info.strip()
        info = info.split("<marker")
        for i in info:
            loc = i.strip()
            loc = loc.rstrip("></marker>")
            if len(loc) > 0:
                title = loc.split('name="')[1].split('"')[0]
                title = title.replace("\\", "")
                title = title.replace("&amp;", "&")
                title = title.strip()
                street = loc.split('street="')[1].split('"')[0]
                street = street.replace("&amp;", "&")
                street = street.replace("\\", "")
                street = street.replace("â€“", "-")
                street = street.strip()
                city = loc.split('city="')[1].split('"')[0]
                city = city.strip()
                state = loc.split('statecode="')[1].split('"')[0]
                state = state.strip()
                pcode = loc.split('postalcode="')[1].split('"')[0]
                pcode = pcode.strip()
                country = loc.split('country="')[1].split('"')[0]
                country = country.strip()
                phone = loc.split('phone="')[1].split('"')[0]
                phone = phone.strip()
                lat = loc.split('lat="')[1].split('"')[0]
                lat = lat.strip()
                lng = loc.split('lng="')[1].split('"')[0]
                lng = lng.strip()
                storeid = loc.split('storeid="')[1].split('"')[0]
                storeid = storeid.strip()
                cat = loc.split('category="')[1].split('"')[0]
                cat = cat.strip()
                name = title
                name = name.replace(" ", "-")
                name = name.replace("(", "")
                name = name.replace(")", "")
                loclink = pagelink + "/location-detail/" + storeid + "/" + name
                loclink = loclink.rstrip(".")
                loclink = loclink.replace("-&-", "-")
                loclink = loclink.replace("&", "-")

                s = session.get(loclink, headers=headers, verify=False)
                soup = BeautifulSoup(s.text, "html.parser")
                div = soup.findAll("div", {"class": "loc-cell"})[1]
                hours = div.text
                hours = hours.strip()
                hours = hours.replace("\n", " ")
                hours = hours.lstrip("Hours")
                hours = hours.strip()
                hours = hours.replace("M2F:", "Mon-Fri:")
                if hours == "Sun:":
                    hours = "<MISSING>"
                if (
                    hours
                    == "Mon-Fri: Tuesday-Friday 8:30 AM - 5:30 PM Sat: 9:00 AM - 5:00 PM Sun: CLOSED"
                ):
                    hours = (
                        "Tues-Fri: 8:30 AM - 5:30 PM Sat: 9:00 AM - 5:00 PM Sun: CLOSED"
                    )
                if (
                    hours
                    == "Mon-Fri: Monday: 10:00am - 6:00pm / Tuesday & Wednesday: 8:00am - 6:00pm / Thursday & Friday: 10:00am - 7:00pm Sat: 8:00am - 6:00pm Sun: Closed"
                ):
                    hours = "Mon: 10:00am - 6:00pm Tues & Wed: 8:00am - 6:00pm Thurs & Fri: 10:00am - 7:00pm Sat: 8:00am - 6:00pm Sun: Closed"
                if (
                    hours
                    == "Mon-Fri: 8:00am - 5:30pm Monday to Thursday / 8:00am - 5:00pm Friday Sat: 8:00am - 12:00pm Sun: Closed"
                ):
                    hours = "Mon-Thurs: 8:00am - 5:30pm Fri: 8:00am - 5:00pm Sat: 8:00am - 12:00pm Sun: Closed"
                if (
                    hours
                    == "Mon-Fri: Mon: Closed | Tues-Thurs: 9am - 6pm | Fri: 9am - 5pm Sat: 10:00am - 3:00pm Sun: Closed"
                ):
                    hours = "Mon: Closed Tues-Thurs: 9am - 6pm Fri: 9am - 5pm Sat: 10:00am - 3:00pm Sun: Closed"
                if (
                    hours
                    == "Mon-Fri: Closed Mondays | Tues-Fri: 10:00am-4:00pm Sat: 9:00am - 1:00pm Sun: Closed"
                ):
                    hours = "Mon: Closed Tues-Fri: 10:00am-4:00pm Sat: 9:00am - 1:00pm Sun: Closed"
                if (
                    hours
                    == "Mon-Fri: 8:00am - 5:30pm (Mon-Wed) 8:00am - 8:00pm (Thurs-Fri) Sat: 9:00am - 4:00pm Sun: Closed"
                ):
                    hours = "Mon-Wed: 8:00am - 5:30pm Thurs-Fri: 8:00am - 8:00pm Sat: 9:00am - 4:00pm Sun: Closed"
                if storeid == "":
                    storeid = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
                if lat == "":
                    lat = "<MISSING>"
                if lng == "":
                    lng = "<MISSING>"
                if country == "Canada":
                    country = "CAN"
                if country == "United States":
                    country = "US"
                data.append(
                    [
                        "https://www.cloverdalepaint.com/",
                        loclink,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        country,
                        storeid,
                        phone,
                        cat,
                        lat,
                        lng,
                        hours,
                    ]
                )
        j = j + 1
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
