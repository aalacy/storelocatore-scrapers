const fs = require('fs-extra');
const path = require('path');
const crawlBot = require('./crawlbot');
const config = require('../config.json');

const canadaClick1 = '.tile-directory-result > div:nth-child(5) > h3 > a';
const canadaClick2 =
  '.tile-directory-result > div.l-accordion.js-accordion.l-region-cont.t-cursor-pointer.js-region-toggle.open > div > div > a';
const usaClick1 =
  '.tile-directory-result > div.l-accordion.js-accordion.l-region-cont.t-cursor-pointer.js-region-toggle.open > div > div > a';

async function crawl() {
  const fileLocation = `${config.General_Settings.filenamePrefix}${
    config.Website_Settings.Marriott.filenameBody
  }.csv`;
  // If a data file exists in our file system, delete current file, then create a new file.
  if (await fs.existsSync(path.join(__dirname, fileLocation))) {
    await fs.unlink(path.join(__dirname, fileLocation));
    await fs.writeFile(path.join(__dirname, fileLocation), config.General_Settings.headerRow);
  } else {
    await fs.writeFile(path.join(__dirname, fileLocation), config.General_Settings.headerRow);
  }
  // Start with Canada
  await crawlBot.startCrawling(canadaClick1, canadaClick2, 'CA', fileLocation);
  // Next to United States
  await crawlBot.startCrawling(usaClick1, undefined, 'USA', fileLocation);
}

crawl();
