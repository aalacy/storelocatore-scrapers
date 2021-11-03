import csv
from sgrequests import SgRequests
from sglogging import sglog

website = "oberweis_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "authority": "oberweis.com",
    "method": "POST",
    "path": "/api/StoreFinder",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-length": "109",
    "content-type": "application/json;charset=UTF-8",
    "cookie": "ASP.NET_SessionId=f2bpeacqxm2zslnguuwo1tvh; _ga=GA1.2.1878780694.1611165405; _gid=GA1.2.1932864939.1611165405; _gcl_au=1.1.1640766567.1611165406; customerId=0; _fbp=fb.1.1611165411823.1887695553; sib_cuid=c1148fb0-1481-4e39-aeef-2b5a650fe546; _pin_unauth=dWlkPU5UWmhaRFV6WTJNdE1XVmlaUzAwTURNNExXRTVORFl0WVdNMk1URXdZVFV5WVdVNA; cookieconsent_status=dismiss; _gat=1; _uetsid=dfe162705b4811ebab738b147d7c30b3; _uetvid=dfe1dce05b4811eb8bde95cf5c676bc9",
    "origin": "https://oberweis.com",
    "referer": "https://oberweis.com/search/find-a-store?oberweisStores=true&groceryStores=true",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        temp_list = []  # ignoring duplicates
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
        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    url = "https://oberweis.com/api/StoreFinder"
    if True:
        myobj = {
            "latitude": "41.79818400000001",
            "longitude": "-88.348431",
            "searchOberweis": "true",
            "searchRetail": "true",
            "distance": "100",
        }
        r = session.post(url, json=myobj, headers=headers)
        oberweis = r.json()["oberweis"]
        retail = r.json()["retail"]
        for loc in oberweis:
            title = loc["name"]
            link = loc["location"]
            link = link.replace(" ", "%20")
            link = "https://oberweis.com/ice-cream-and-dairy-stores/" + link
            street = loc["address"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["zipCode"]
            if not pcode:
                pcode = "<MISSING>"
            longt = loc["coordinates"]["longitude"]
            lat = loc["coordinates"]["latitude"]
            hours = loc["description"]
            hours = hours.replace("<br>", " ").replace("<b>", "").replace("</b>", " ")
            hours = hours.split("Store Hours", 1)
            phone = hours[0].split("Phone:", 1)[1].split("Email", 1)[0].strip()
            hours = hours[1].strip()
            data.append(
                [
                    "https://oberweis.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )
        for loc in retail:
            title = loc["name"]
            street = loc["address"]
            if not street:
                street = "<MISSING>"
            city = loc["city"]
            if not city:
                city = "<MISSING>"
            state = loc["state"]
            pcode = loc["zipCode"]
            if not pcode:
                pcode = "<MISSING>"
            longt = loc["coordinates"]["longitude"]
            lat = loc["coordinates"]["latitude"]
            data.append(
                [
                    "https://oberweis.com/",
                    "https://oberweis.com/search/find-a-store",
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    lat,
                    longt,
                    "<MISSING>",
                ]
            )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
