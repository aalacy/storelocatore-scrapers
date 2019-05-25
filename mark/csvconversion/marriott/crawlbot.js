'use strict';

const   puppeteer   = require('puppeteer'),
        fs          = require('fs-extra'),
        converter   = require('../lib/converter'),
        config      = require('../config.json'),
        moment      = require('moment'),
        path        = require('path');

async function startCrawling(initialClick, secondaryClick, country, fileLocation) {

    const click1        = initialClick,
          click2        = secondaryClick,
          fileLocationMemory  = fileLocation;
    
    try {

        const browser = await puppeteer.launch({ headless: config.General_Settings.headless });
        const context = await browser.createIncognitoBrowserContext();
        const page = await context.newPage();
        const marriottDirectory = 'https://www.marriott.com/hotel-search.mi';
    
        //Setting to mimic a real user of the browser. Google search 'check user agent' to get your own.
        await page.setUserAgent(config.General_Settings.userAgent);

        await page.goto(marriottDirectory);
    
        //Waits for Canada Selector before proceeding to search page
        await page.waitForSelector('.l-accordion');
        if (click1) { await page.click(click1); }
        if (click2 && click2.length > 0) { await page.click(click2); }

        //Enter search page, then wait for pagination last page
        await page.waitForSelector('#results-pagination > div > div.l-display-inline-block > a:nth-child(5)');

        //Get the pagination and use to loop through each page
        const lastPageString = await page.$eval('#results-pagination > div > div.l-display-inline-block > a:nth-child(5)', (div) => { return div.innerText });
        const lastPage = parseInt(lastPageString, 10);

        for (let i = 1; i <= lastPage; i++) {

            //Wait for list of properties to appear
            await page.waitForSelector('.property-record-item');
            await page.waitForSelector('.js-property-list-container > div > div > div > div.js-hotel-location > div > div.m-hotel-address');

            //Data is split with an outer div and inner div -> start with outer
            const dataPropertyOuter = await page.evaluate(() => 
                Array.from(document.body.querySelectorAll('.js-property-list-container > div'), 
                    (div) => {
                        return JSON.parse(div.dataset['property'])
                    }
                )
            );

            //Inner div data
            const dataPropertyInner = await page.evaluate(() =>
                Array.from(document.body.querySelectorAll('.js-property-list-container > div > div > div > div.js-hotel-location > div > div.m-hotel-address'), 
                    (div) => {
                        return {
                            address: div.dataset['addressLine1'],
                            postalCode: div.dataset['postalCode'],
                            city: div.dataset['city'],
                            state: div.dataset['state'],
                            country: div.dataset['countryDescription'],
                            phoneNumber: div.dataset['contact']
                        }
                    }
                )
            );

            //Array requires formatting because number has spaces / punctuation and zip code has a space. 
            const formattedDataPropertyInner = converter.formatInnerArray(dataPropertyInner);

            //Combine outer and inner div objects and return data before moving on
            const dataProperty = converter.combineObjArray(dataPropertyOuter, formattedDataPropertyInner);

            // Loop to insert each row into the .CSV -> Possible to rework in future, if necessary
            for await (let obj of dataProperty){
                let locatorDomain       = 'marriott.com__search__findHotels.mi',
                    locationName        = obj.hotelName,
                    streetAddress       = obj.address,
                    city                = obj.city,
                    state               = obj.state,
                    zip                 = obj.postalCode,
                    countryCode         = obj.country,
                    storeNumber         = 'NO-DATA',
                    phone               = obj.phoneNumber,
                    locationType        = obj.brand,
                    naics               = 'NO-DATA',
                    latitude            = obj.lat,
                    longitude           = obj.longitude,
                    hours_of_operation  = 'NO-DATA'

                await fs.appendFile(
                    path.join(__dirname, fileLocationMemory), 
                    `"${locatorDomain}","${locationName}","${streetAddress}","${city}","${state}","${zip}","${countryCode}","${storeNumber}","${phone}","${locationType}","${naics}","${latitude}","${longitude}","${hours_of_operation}"\n`
                );
            }
            if (i === lastPage) {
                break;
            } else {
                //Click Next Page
                await page.waitForSelector('#results-pagination > div > div.l-display-inline-block > a.m-pagination-next');
                await page.click(' #results-pagination > div > div.l-display-inline-block > a.m-pagination-next');
                await page.waitFor(config.General_Settings.delayTime);
            }     
        }

        await browser.close(); 

    } catch (error) {
        console.log(error);
    }

}

module.exports = {
    startCrawling
}