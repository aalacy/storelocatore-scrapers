import csv
import sgrequests
import bs4
import re


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    # Your scraper here
    locator_domain = "https://theory.com/"

    wanted_domains = [
        "https://www.theory.com/on/demandware.store/Sites-theory2_US-Site/default/Stores-FindStores?country=US&",
        "https://www.theory.com/on/demandware.store/Sites-theory2_US-Site/default/Stores-FindStores?country=GB&",
    ]

    store_urls = []

    def spider(link, arr):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
        }
        sess = bs4.BeautifulSoup(
            sgrequests.SgRequests().get(link, headers=header).text, features="lxml"
        )
        for ide in sess.findAll("li", {"class": "js-store-item hide"}):
            url = f"https://www.theory.com/storedetail/?StoreID={ide['data-store-resultitem']}"
            arr.append(url)

    spider(wanted_domains[0], store_urls)
    spider(wanted_domains[1], store_urls)

    con = set(store_urls)

    result = []

    missingString = "<MISSING>"

    def getSoup(link):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
        }
        txt = sgrequests.SgRequests().get(link, headers=header).text
        return [txt, bs4.BeautifulSoup(txt, features="lxml")]

    for ss in con:
        sss = getSoup(ss)
        s = sss[1]
        res = s.find("div", {"class": "js-store-item hide"})
        name = res["data-store-name"]
        street = res["data-store-address1"]
        city = res["data-store-city"]
        zp = missingString
        if (
            s.find("div", {"class": "city-zip-code"})
            .text.split(" ")[-1]
            .strip()
            .isdigit()
        ):
            zp = s.find("div", {"class": "city-zip-code"}).text.split(" ")[-1].strip()
        else:
            zp = (
                s.find("div", {"class": "city-zip-code"}).text.split(" ")[-2].strip()
                + " "
                + s.find("div", {"class": "city-zip-code"}).text.split(" ")[-1].strip()
            )
        if "data-store-postalCode" in res:
            zp = res["data-store-postalCode"]
        store_num = res["data-store-resultitem"]
        country = res["data-store-country"]
        phone = res["data-store-phone"]
        loc_type = res["data-store-type"]
        lat = res["data-store-latitude"]
        lng = res["data-store-longitude"]

        p = s.findAll("p")

        timeArr = []

        for ps in p:
            if "Monday" in ps.text:
                timeArr.append(ps.text.strip("\n"))
            elif "Tuesday" in ps.text:
                timeArr.append(ps.text.strip("\n"))
            elif "Wednesday" in ps.text:
                timeArr.append(ps.text.strip("\n"))
            elif "Thursday" in ps.text:
                timeArr.append(ps.text.strip("\n"))
            elif "Friday" in ps.text:
                timeArr.append(ps.text.strip("\n"))
            elif "Saturday" in ps.text:
                timeArr.append(ps.text.strip("\n"))
            elif "Sunday" in ps.text:
                timeArr.append(ps.text.strip("\n"))

        hours = ", ".join(timeArr).strip("\n")

        if hours == "":
            for el in s.findAll("div", {"class": "details-info"}):
                if "Monday" in el.text.strip():
                    h = el.text
                    t = []
                    for l in h.splitlines():
                        t.append(l.strip())
                    hours = ", ".join(t).replace(",", "", 1)[:-2]
                else:
                    pass

        if loc_type == "":
            loc_type = missingString

        code = re.search(r'"DEFAULT_COUNTRY_CODE":"(.*?)",', sss[0]).group(1)

        result.append(
            [
                locator_domain,
                ss,
                name,
                street,
                city,
                country,
                zp,
                code,
                store_num,
                phone,
                loc_type,
                lat,
                lng,
                hours.strip("\n").strip(),
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
