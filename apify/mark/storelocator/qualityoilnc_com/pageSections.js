const Apify = require('apify');

const {
  locationNameSelector,
  addressSelector,
  phoneSelector,
  geoSelector,
  hourSelector,
} = require('./selectors');

const {
  formatAddress,
  formatPhoneNumber,
  parseGoogleMapsUrl,
} = require('./tools');

const {
  Poi,
} = require('./Poi');

const qualityMartScrape = async (page) => {
  const contentId = '#panel621';
  const contentSelector = `${contentId} .locationsList .columns`;
  const contentColumns = await page.$$(contentSelector);
  /* eslint-disable no-restricted-syntax */
  for await (const content of contentColumns) {
    // One of the columns has no content and throws an error, so we must check
    if (await content.$('h6') !== null) {
      /* eslint-disable camelcase */
      const location_name = await content.$eval(locationNameSelector, e => e.innerText);
      const addressRaw = await content.$eval(addressSelector, e => e.innerHTML);
      const phoneRaw = await content.$eval(phoneSelector, e => e.innerText);
      const geoRaw = await content.$eval(geoSelector, e => e.getAttribute('href'));
      const hours = await content.$eval(hourSelector, e => e.innerText);
      const addressBlock = formatAddress(addressRaw);
      const latLong = parseGoogleMapsUrl(geoRaw);
      const poiData = {
        locator_domain: 'qualityoilnc.com',
        location_name,
        ...addressBlock,
        phone: formatPhoneNumber(phoneRaw),
        location_type: 'Quality Mart',
        ...latLong,
        hours_of_operation: hours,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    }
  }
};

const qualityPlusScrape = async (page) => {
  const contentId = '#panel624';
  const contentSelector = `${contentId} .locationsList .columns`;
  const contentColumns = await page.$$(contentSelector);
  /* eslint-disable no-restricted-syntax */
  for await (const content of contentColumns) {
    // One of the columns has no content and throws an error, so we must check
    if (await content.$('h6') !== null) {
      /* eslint-disable camelcase */
      const location_name = await content.$eval(locationNameSelector, e => e.innerText);
      const addressRaw = await content.$eval(addressSelector, e => e.innerHTML);
      const phoneRaw = await content.$eval(phoneSelector, e => e.innerText);
      const geoRaw = await content.$eval(geoSelector, e => e.getAttribute('href'));
      const addressBlock = formatAddress(addressRaw);
      const latLong = parseGoogleMapsUrl(geoRaw);
      const poiData = {
        locator_domain: 'qualityoilnc.com',
        location_name,
        ...addressBlock,
        phone: formatPhoneNumber(phoneRaw),
        location_type: 'Quality Plus',
        ...latLong,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    }
  }
};

const goGasScrape = async (page) => {
  const contentId = '#panel4144';
  const contentSelector = `${contentId} .locationsList .columns`;
  const contentColumns = await page.$$(contentSelector);
  /* eslint-disable no-restricted-syntax */
  for await (const content of contentColumns) {
    // One of the columns has no content and throws an error, so we must check
    if (await content.$('h6') !== null) {
      /* eslint-disable camelcase */
      const location_name = await content.$eval(locationNameSelector, e => e.innerText);
      const addressRaw = await content.$eval(addressSelector, e => e.innerHTML);
      const phoneRaw = await content.$eval(phoneSelector, e => e.innerText);
      const geoRaw = await content.$eval(geoSelector, e => e.getAttribute('href'));
      const addressBlock = formatAddress(addressRaw);
      const latLong = parseGoogleMapsUrl(geoRaw);
      const poiData = {
        locator_domain: 'qualityoilnc.com',
        location_name,
        ...addressBlock,
        phone: formatPhoneNumber(phoneRaw),
        location_type: 'GOGAS',
        ...latLong,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    }
  }
};

const hospitalityScrape = async (page) => {
  const contentId = '#panel619';
  const contentSelector = `${contentId} .locationsList .columns`;
  const contentColumns = await page.$$(contentSelector);
  /* eslint-disable no-restricted-syntax */
  for await (const content of contentColumns) {
    // One of the columns has no content and throws an error, so we must check
    if (await content.$('h6') !== null) {
      /* eslint-disable camelcase */
      const location_name = await content.$eval(locationNameSelector, e => e.innerText);
      const addressRaw = await content.$eval(addressSelector, e => e.innerHTML);
      const phoneRaw = await content.$eval(phoneSelector, e => e.innerText);
      const geoRaw = await content.$eval(geoSelector, e => e.getAttribute('href'));
      const addressBlock = formatAddress(addressRaw);
      const latLong = parseGoogleMapsUrl(geoRaw);
      const poiData = {
        locator_domain: 'qualityoilnc.com',
        location_name,
        ...addressBlock,
        phone: formatPhoneNumber(phoneRaw),
        location_type: 'Quality Hospitality',
        ...latLong,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    }
  }
};

const serviceScrape = async (page) => {
  const contentId = '#panel849';
  const contentSelector = `${contentId} .locationsList .columns`;
  const contentColumns = await page.$$(contentSelector);
  /* eslint-disable no-restricted-syntax */
  for await (const content of contentColumns) {
    // One of the columns has no content and throws an error, so we must check
    if (await content.$('h6') !== null) {
      /* eslint-disable camelcase */
      const location_name = await content.$eval(locationNameSelector, e => e.innerText);
      const addressRaw = await content.$eval(addressSelector, e => e.innerHTML);
      const phoneRaw = await content.$eval(phoneSelector, e => e.innerText);
      const geoRaw = await content.$eval(geoSelector, e => e.getAttribute('href'));
      const addressBlock = formatAddress(addressRaw);
      const latLong = parseGoogleMapsUrl(geoRaw);
      const poiData = {
        locator_domain: 'qualityoilnc.com',
        location_name,
        ...addressBlock,
        phone: formatPhoneNumber(phoneRaw),
        location_type: 'Service Station',
        ...latLong,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    }
  }
};

const tankLineScrape = async (page) => {
  const contentId = '#panel1234';
  const contentSelector = `${contentId} .locationsList .columns`;
  const contentColumns = await page.$$(contentSelector);
  /* eslint-disable no-restricted-syntax */
  for await (const content of contentColumns) {
    // One of the columns has no content and throws an error, so we must check
    if (await content.$('h6') !== null) {
      /* eslint-disable camelcase */
      const location_name = await content.$eval(locationNameSelector, e => e.innerText);
      const addressRaw = await content.$eval(addressSelector, e => e.innerHTML);
      const phoneRaw = await content.$eval(phoneSelector, e => e.innerText);
      const geoRaw = await content.$eval(geoSelector, e => e.getAttribute('href'));
      const addressBlock = formatAddress(addressRaw);
      const latLong = parseGoogleMapsUrl(geoRaw);
      const poiData = {
        locator_domain: 'qualityoilnc.com',
        location_name,
        ...addressBlock,
        phone: formatPhoneNumber(phoneRaw),
        location_type: 'Reliable Tank Line',
        ...latLong,
      };
      const poi = new Poi(poiData);
      await Apify.pushData(poi);
    }
  }
};

module.exports = {
  qualityMartScrape,
  qualityPlusScrape,
  goGasScrape,
  hospitalityScrape,
  serviceScrape,
  tankLineScrape,
};
