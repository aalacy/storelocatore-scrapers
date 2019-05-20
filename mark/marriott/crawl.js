'use strict';

const crawlBot = require('./crawlbot');

const canadaClick1 = '.tile-directory-result > div:nth-child(5) > h3 > a';
const canadaClick2 = '.tile-directory-result > div.l-accordion.js-accordion.l-region-cont.t-cursor-pointer.js-region-toggle.open > div > div > a';
const usaClick1 = '.tile-directory-result > div.l-accordion.js-accordion.l-region-cont.t-cursor-pointer.js-region-toggle.open > div > div > a';

async function crawl() {
    //Start with Canada
    await crawlBot.startCrawling(canadaClick1, canadaClick2, 'CA');
    //Next to United States
    await crawlBot.startCrawling(usaClick1, undefined, 'USA');
}

crawl();