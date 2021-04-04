import csv
import sgrequests
import bs4
import json
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
    locator_domain = "https://store.ferragamo.com/"

    missingString = "<MISSING>"

    wanted_domains = [
        "https://store.ferragamo.com/en-us/america/us.html",
        "https://store.ferragamo.com/en-us/america/ca.html",
        "https://store.ferragamo.com/en-us/europe/gb/greater-london/london.html",
    ]

    res = []

    sess = sgrequests.SgRequests()

    one = bs4.BeautifulSoup(sess.get(wanted_domains[0]).text, features="lxml").findAll(
        "a", {"class": "c-directory-list-content-item-link"}
    )
    two = bs4.BeautifulSoup(sess.get(wanted_domains[1]).text, features="lxml").findAll(
        "a", {"class": "c-directory-list-content-item-link"}
    )
    three = bs4.BeautifulSoup(
        sess.get(wanted_domains[2]).text, features="lxml"
    ).findAll("a", {"class": "Teaser-link Teaser-linkPage"})

    for o in one:
        res.append(o["href"])

    for t in two:
        res.append(t["href"])

    for th in three:
        res.append(th["href"])

    def spider(link):
        req = bs4.BeautifulSoup(sess.get(link).text, features="lxml")
        if req.find("div", {"itemprop": "description"}):
            return {"status": "Store", "url": link}
        else:
            return {"status": None, "url": link}

    stores = []

    for u in res:
        url = locator_domain + u.replace("../", "")
        s = spider(url)
        if s["status"] is None:
            urls = bs4.BeautifulSoup(sess.get(s["url"]).text, features="lxml")
            dir_link = urls.findAll(
                "a", {"class": "c-directory-list-content-item-link"}
            )
            if not dir_link:
                teaser_link = urls.findAll(
                    "a", {"class": "Teaser-link Teaser-linkPage"}
                )
                if not teaser_link:
                    pass
                else:
                    for link in teaser_link:
                        urlll = locator_domain + link["href"].replace("../", "")
                        sss = spider(urlll)
                        if sss is None:
                            pass
                        else:
                            stores.append(sss["url"])
            else:
                for ls in dir_link:
                    urll = locator_domain + ls["href"].replace("../", "")
                    ss = spider(urll)
                    if ss["status"] is None:
                        ssoup = bs4.BeautifulSoup(
                            sess.get(ss["url"]).text, features="lxml"
                        ).findAll("a", {"class": "Teaser-link Teaser-linkPage"})
                        for l in ssoup:
                            urlll = locator_domain + l["href"].replace("../", "")
                            stores.append(urlll)
                    else:
                        stores.append(ss["url"])
        else:
            stores.append(s["url"])

    result = []

    def generateHourString(hour):
        return str(hour)[:2] + ":" + str(hour)[2:]

    for store in stores:
        a = sess.get(store).text
        st = bs4.BeautifulSoup(a, features="lxml")
        name = missingString
        if st.find("span", {"class": "Hero-title Heading--lead"}):
            name = st.find("span", {"class": "Hero-title Heading--lead"}).text
        else:
            name = missingString
        street = st.find("span", {"class": "c-address-street-1"}).text
        city = st.find("span", {"class": "c-address-city"}).text
        state = missingString
        if st.find("abbr", {"class": "c-address-state"}):
            state = st.find("abbr", {"class": "c-address-state"}).text
        zc = st.find("span", {"class": "c-address-postal-code"}).text
        lat = st.find("meta", {"itemprop": "latitude"})["content"]
        lng = st.find("meta", {"itemprop": "longitude"})["content"]
        phone = st.find("a", {"data-ya-track": "mobile_phone_call"}).text
        time = json.loads(
            st.find(
                "div", {"class": "c-location-hours-details-wrapper js-location-hours"}
            )["data-days"]
        )
        array = []
        for obj in time:
            if len(obj["intervals"]) == 0:
                array.append(f"{obj['day']} Closed")
            else:
                array.append(
                    f"{obj['day']} {generateHourString(obj['intervals'][0]['start'])} AM - {generateHourString(obj['intervals'][0]['end'])} PM"
                )
        hour = ", ".join(array)
        country_code = re.search(r'"country":"(.*?)",', a).group(1)
        store_num = re.search(r'"id":(.*?),', a).group(1)
        result.append(
            [
                locator_domain,
                store,
                name,
                street,
                city,
                state,
                zc,
                country_code,
                store_num,
                phone,
                missingString,
                lat,
                lng,
                hour,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
