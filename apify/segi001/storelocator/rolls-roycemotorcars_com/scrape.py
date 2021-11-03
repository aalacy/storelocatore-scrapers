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
    locator_domain = "https://www.rolls-roycemotorcars.com/"
    missingString = "<MISSING>"

    def initSoup(link):
        return bs4.BeautifulSoup(
            sgrequests.SgRequests().get(link).text, features="lxml"
        )

    def sendReq(link):
        return sgrequests.SgRequests().get(link)

    def linkIsValid(link):
        if "https://www.rolls-roycemotorcars.com/" in link:
            return True
        else:
            return False

    def retrieveLinks():
        # @returns an array
        res = []
        s = initSoup("https://www.rolls-roycemotorcars.com/en_GB/dealers/site-map.html")
        for l in s.findAll("a", {"target": "_blank"}, href=True):
            if not linkIsValid(l["href"]):
                pass
            else:
                res.append(
                    {
                        "link": l["href"],
                        "name": l.text.strip(),
                        "city": l.text.strip()
                        .replace("Showroom", "")
                        .replace("Services", ""),
                    }
                )
        return res

    def countryValidator(storeArr, cityArr):
        # @returns an array of valid links for certain country
        def returnValidJson(storeArr, cityArr):
            res = []
            for storeJson in storeArr:
                storeCity = storeJson["city"].title().strip().title()
                for d in cityArr:
                    validatorCity = d["city"].title().strip()
                    validatorCountry = d["country"].strip()
                    if (
                        "United Kingdom of Great Britain and Northern Ireland"
                        in validatorCountry
                    ):
                        if (
                            validatorCity in storeCity
                            or storeCity in validatorCity
                            or storeCity == validatorCity
                            or validatorCity == storeCity
                        ):
                            res.append(
                                {
                                    "name": storeJson["name"],
                                    "city": storeJson["city"],
                                    "country": validatorCountry,
                                    "link": storeJson["link"],
                                }
                            )
                    else:
                        if "en_US" in storeJson["link"]:
                            res.append(
                                {
                                    "name": storeJson["name"],
                                    "city": storeJson["city"],
                                    "country": None,
                                    "link": storeJson["link"],
                                }
                            )
                        elif "United States of America" in validatorCountry:
                            if (
                                validatorCity in storeCity
                                or storeCity in validatorCity
                                or storeCity == validatorCity
                                or validatorCity == storeCity
                            ):
                                res.append(
                                    {
                                        "name": storeJson["name"],
                                        "city": storeJson["city"],
                                        "country": None,
                                        "link": storeJson["link"],
                                    }
                                )
                        elif "Canada" in validatorCountry:
                            if (
                                validatorCity in storeCity
                                or storeCity in validatorCity
                                or storeCity == validatorCity
                                or validatorCity == storeCity
                            ):
                                res.append(
                                    {
                                        "name": storeJson["name"],
                                        "city": storeJson["city"],
                                        "country": None,
                                        "link": storeJson["link"],
                                    }
                                )
                if "Alberta" in storeJson["name"]:
                    res.append(
                        {
                            "name": storeJson["name"],
                            "city": storeJson["city"],
                            "country": None,
                            "link": storeJson["link"],
                        }
                    )
                if "Sao Paulo" in storeJson["name"]:
                    res.append(
                        {
                            "name": storeJson["name"],
                            "city": storeJson["city"],
                            "country": None,
                            "link": storeJson["link"],
                        }
                    )
            return res

        string_res = []
        for e in returnValidJson(storeArr, cityArr):
            string_res.append(json.dumps(e))
        new_res = []
        for ele in set(string_res):
            new_res.append(json.loads(ele))
        return new_res

    allCities = json.loads(
        sendReq("https://countriesnow.space/api/v0.1/countries/population/cities").text
    )["data"]

    s = countryValidator(retrieveLinks(), allCities)

    result = []

    def checkDuplicate(l):
        for e in result:
            if l in e:
                return True
        return False

    for ss in s:
        bs = initSoup(ss["link"])
        if not bs.find("div", {"class": "rrmc-find-us--address"}):
            pass
        elif "/perth/" in ss["link"]:
            pass
        else:
            name = ss["name"]
            city = ss["city"]
            country = missingString
            findUs = (
                bs.find("div", {"class": "rrmc-find-us--address"})
                .findAll("span")[1]
                .text.split(",")
            )
            zp = findUs[-1]
            state = findUs[-2]
            street = findUs[0]
            url = ss["link"]
            if "Scotland" in zp or "United Kingdom" in zp or "Brazil" in zp:
                zp = findUs[-3]
                state = findUs[-2]
            else:
                zp = findUs[-1]
                state = findUs[-2]
            phone = (
                bs.find("a", {"data-channel": "telephone"})
                .text.strip()
                .replace("Tel:", "")
            )
            timeArray = []
            hours = bs.findAll("div", {"class": "rrmc-find-us--opening-hours-entry"})
            for hs in hours:
                timeArray.append(hs.text.strip().replace(u"\n", ""))
            h = re.sub(r"\s{2,}", ", ", ", ".join(timeArray))
            if checkDuplicate(name):
                pass
            else:
                result.append(
                    [
                        locator_domain,
                        url,
                        name,
                        street,
                        city,
                        state,
                        zp,
                        country,
                        missingString,
                        phone,
                        missingString,
                        missingString,
                        missingString,
                        h,
                    ]
                )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
