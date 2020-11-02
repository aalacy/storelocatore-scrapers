const Apify = require('apify');
const {
  enqueueDetailPages,
} = require('./routes');

const {
  addressSelector,
  geoSelector,
} = require('./selectors');

const {
  formatAddress,
  formatPhoneNumber,
  parseGoogleMapsUrl,
  formatHours,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: 'http://westernbeef.com/western-beef---locations.html',
    userData: {
      urlType: 'initial',
    },
  });

  const crawler = new Apify.PuppeteerCrawler({
    requestQueue,
    handlePageFunction: async ({ request, page }) => {
      // Site has inner layers that also have details links
      if (request.userData.urlType === 'initial') {
        await page.waitFor(2000);
        await enqueueDetailPages({ page }, { requestQueue });
      }
      if (request.userData.urlType === 'detail') {
        const imgAlts = await page.$$eval(addressSelector, se => se.map(e => e.getAttribute('alt')));
        const addressRaw = imgAlts.filter(e => e !== null && e.length > 10)[0];
        const addressObject = formatAddress(addressRaw);
        if (addressObject.street_address) {
          // Check if they use an image for location info
          // Paragraph or span has the info
          const allSpan = await page.$$eval('span', se => se.map(s => s.innerText));
          const allPTags = await page.$$eval('p', pe => pe.map(p => p.innerText));
          const checkPhoneValueSpan = allSpan.filter(e => e.includes('Telephone'));
          const checkPhoneValuePTag = allPTags.filter(e => e.includes('Telephone'));
          let phoneRaw;
          let hoursRaw;
          if (checkPhoneValueSpan.length > 0) {
            // Image is not used, so parse normally
            [phoneRaw] = checkPhoneValueSpan;
            const indexOfHours = allPTags.findIndex(e => e.includes('Hours')) + 1;
            const indexOfEnd = allPTags.findIndex(e => e.includes('Contact'));
            const hoursArray = allPTags.slice(indexOfHours, indexOfEnd);
            hoursRaw = hoursArray.join(', ');
          }
          if (checkPhoneValuePTag.length > 0) {
            [phoneRaw] = checkPhoneValuePTag;
            const indexOfHours = allPTags.findIndex(e => e.includes('Hours')) + 1;
            const indexOfEnd = allPTags.findIndex(e => e.includes('Contact'));
            const hoursArray = allPTags.slice(indexOfHours, indexOfEnd);
            hoursRaw = hoursArray.join(', ');
          }
          if (checkPhoneValuePTag.length === 0 || checkPhoneValueSpan === 0) {
            // Image is used, so grab the image alt for info
            const allImgAlts = await page.$$eval(addressSelector, se => se.map(e => e.getAttribute('alt')));
            const regexHours = /hours/i;
            const imgInfoArray = allImgAlts.filter(e => regexHours.test(e));
            const imgInfoString = imgInfoArray[0];
            // Some images don't have phone numbers
            if (imgInfoString.includes('Telephone')) {
              const hourString = imgInfoString.match(regexHours);
              const hoursIndex = imgInfoString.indexOf(hourString);
              hoursRaw = imgInfoString.substring((hoursIndex + 6), imgInfoString.indexOf('Contact'));
              phoneRaw = imgInfoString.substring(imgInfoString.indexOf('Telephone'), imgInfoString.length);
            } else {
              hoursRaw = imgInfoString.substring((imgInfoString.indexOf('Hours') + 6), imgInfoString.length);
              phoneRaw = undefined;
            }
          }
          const frame = await page.frames();
          const googleIframe = frame[1];
          await page.waitFor(5000);
          await googleIframe.waitForSelector(geoSelector);
          const geoTags = await googleIframe.$eval(geoSelector, a => a.getAttribute('href'));
          const latLong = parseGoogleMapsUrl(geoTags);
          const poiData = {
            locator_domain: 'westernbeef.com',
            ...addressObject,
            phone: formatPhoneNumber(phoneRaw),
            country_code: undefined,
            ...latLong,
            hours_of_operation: formatHours(hoursRaw),
          };
          const poi = new Poi(poiData);
          await Apify.pushData(poi);
        }
      }
    },
    maxRequestsPerCrawl: 50,
    maxConcurrency: 1,
    launchPuppeteerOptions: { headless: true, args: ['--disable-features=site-per-process'] },
    gotoFunction: async ({
      request, page,
    }) => page.goto(request.url, {
        timeout: 0, waitUntil: 'networkidle0',
      }),
  });

  await crawler.run();
});

module.exports = {
  Apify,
};
