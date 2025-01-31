const puppeteer = require("puppeteer-extra");
const launch = require("./launch");
const fs = require('fs');

// Wait function
const wait = (ms) => new Promise(res => setTimeout(res, ms));

// Convert timestamp to HH:MM:SS
function convertTimestampToHour(timestamp) {
    const date = new Date(timestamp);
    const hours = ('0' + date.getHours()).slice(-2);
    const minutes = ('0' + date.getMinutes()).slice(-2);
    const seconds = ('0' + date.getSeconds()).slice(-2);
    return `${hours}:${minutes}:${seconds}`;
}

// Function to get the day number (Monday = 1, ..., Sunday = 7)
function getDayNumber(timestamp) {
    const date = new Date(timestamp);
    return (date.getDay() === 0) ? 7 : date.getDay(); // Convert Sunday (0) to 7
}

// **Fix: Define getWsEndpoint function**
async function getWsEndpoint() {
    return await launch();
}

// Ensure the CSV file has headers only once
const csvFilePath = 'data.csv';
if (!fs.existsSync(csvFilePath) || fs.statSync(csvFilePath).size === 0) {
    fs.writeFileSync(csvFilePath, "Day,Round,Time,NumberOfPlayers,TotalBet,TotalWinning,OnCrash\n");
}

(async () => {
    const browser = await puppeteer.connect({
        browserWSEndpoint: await getWsEndpoint(),
        defaultViewport: null,
    });

    const page = await browser.newPage();
    await page.goto("https://1xbet.com/en/allgamesentrance/crash", { timeout: 60000 });

    const client = await page.target().createCDPSession();
    await client.send('Network.enable');

    let round = 1;
    let roundData = {
        OnStart: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
        OnCashouts: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
        OnCrash: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
        OnBets: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 }
    };

    client.on('Network.webSocketFrameReceived', ({ response }) => {
        let payloadString = response.payloadData.toString('utf8');

        try {
            payloadString = payloadString.replace(/[^\x20-\x7E]/g, "");
            const payload = JSON.parse(payloadString);

            if (payload.target && roundData[payload.target]) {
                const eventType = payload.target;
                const eventData = payload.arguments[0];

                const timestamp = eventData.ts || Date.now();
                roundData[eventType].time = convertTimestampToHour(timestamp);
                roundData[eventType].numberOfPlayers = eventData.n || 0;

                if (eventType === 'OnBets') {
                    roundData[eventType].totalBet = eventData.bid || 0;
                } else if (eventType === 'OnCashouts') {
                    roundData[eventType].totalWinning = eventData.won || 0;
                } else {
                    roundData[eventType].totalBet = eventData.l || 0;
                    roundData[eventType].totalWinning = eventData.f || 0;
                }

                // **NEW: Delay capturing TotalWinning until AFTER OnCrash**
                if (eventType === 'OnCrash') {
                    setTimeout(() => {
                        const dayNumber = getDayNumber(timestamp);

                        // **Ensure we capture winnings AFTER OnCrash**
                        const totalWinningAfterCrash = roundData.OnCashouts.totalWinning; // Final value

                        const csvData = `${dayNumber},${round},${roundData.OnStart.time},${roundData.OnCashouts.numberOfPlayers},${roundData.OnBets.totalBet.toFixed(2)},${totalWinningAfterCrash.toFixed(2)},${roundData.OnCrash.totalWinning.toFixed(2)}\n`;

                        fs.appendFile(csvFilePath, csvData, (err) => {
                            if (err) console.error('Error writing to file:', err);
                        });

                        // Reset round data
                        round++;
                        roundData = {
                            OnStart: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
                            OnCashouts: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
                            OnCrash: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
                            OnBets: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 }
                        };
                    }, 500); // **500ms delay to ensure no slips in TotalWinning**
                }
            }
        } catch (error) {
            console.error('Error processing WebSocket frame:', error);
        }
    });

    // Keep the browser active
    while (true) {
        await page.keyboard.press("Tab");
        await wait(1000);
        await page.keyboard.press("ArrowDown");
        await wait(1000);
    }
})();
