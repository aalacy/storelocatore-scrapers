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
    locator_domain = "https://www.scotch-soda.com/"

    wanted_domains = [
        "https://stores.scotch-soda.com/united-kingdom/greater-london/london",
        "https://stores.scotch-soda.com/united-states",
        "https://stores.scotch-soda.com/canada",
    ]

    missingString = "<MISSING>"

    store_array = []

    def spider(link, arr):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
        }
        sess = sgrequests.SgRequests()

        def hasLinks(site):
            obj = bs4.BeautifulSoup(
                sess.get(site, headers=headers).text, features="lxml"
            )
            if obj.find("a", {"class": "c-directory-list-content-item-link"}):
                s = obj.findAll("a", {"class": "c-directory-list-content-item-link"})
                for l in s:
                    url = f"https://stores.scotch-soda.com/{l['href']}"
                    hasLinks(url)
            elif obj.find("a", {"data-ya-track": "visitsite"}):
                l = obj.findAll("a", {"data-ya-track": "visitsite"})
                for ll in l:
                    url = (
                        f"https://stores.scotch-soda.com/{ll['href'].replace('../','')}"
                    )
                    hasLinks(url)
            elif obj.find("div", {"class": "About-description"}):
                arr.append(site)

        hasLinks(link)

    spider(wanted_domains[0], store_array)
    spider(wanted_domains[1], store_array)
    spider(wanted_domains[2], store_array)

    con = set(store_array)

    def getSoup(link):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
        }
        sess = sgrequests.SgRequests().get(link, headers=headers).text
        return [sess, bs4.BeautifulSoup(sess, features="lxml")]

    result = []

    def isClosed(hours):
        if hours.count("Closed") == 7:
            return True
        else:
            return False

    for store in con:
        soup = getSoup(store)
        s = soup[1]
        name = f"{s.find('span',{'class':'Nap-name Heading Heading--4'}).text} {s.find('span',{'class':'Nap-geomod Heading Heading--1'}).text}"
        street = f"{s.find('span',{'class':'c-address-street-1'}).text}"
        if s.find("span", {"class": "c-address-street-2"}):
            street = f"{s.find('span',{'class':'c-address-street-1'}).text} {s.find('span',{'class':'c-address-street-2'}).text}"
        city = f"{s.find('span',{'class':'c-address-city'}).text}"
        zp = f"{s.find('span',{'class':'c-address-postal-code'}).text}"
        phone = f"{s.find('a',{'class':'c-phone-number-link c-phone-main-number-link'}).text}"
        lat = f"{s.find('meta',{'itemprop':'latitude'})['content']}"
        lng = f"{s.find('meta',{'itemprop':'longitude'})['content']}"
        state = missingString
        if s.find("span", {"itemprop": "addressRegion"}):
            state = f"{s.find('span',{'itemprop':'addressRegion'}).text}"
        code = f"{s.find('address',{'id':'address'})['data-country']}"
        time = s.findAll("tr", {"data-day-of-week-start-index": True})
        timeArr = []
        for t in time:
            timeArr.append(t.text.strip())
        hours = ", ".join(timeArr)
        location_type = missingString
        if isClosed(hours):
            location_type = "Closed"
        store_num = re.search(r'"id":(.*?),', soup[0]).group(1)
        result.append(
            [
                locator_domain,
                store,
                name,
                street,
                city,
                state,
                zp,
                code,
                store_num,
                phone,
                location_type,
                lat,
                lng,
                hours,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
