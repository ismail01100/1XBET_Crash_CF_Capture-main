const puppeteer = require("puppeteer-extra");
const launch = require("./launch");
const fs = require('fs');
const wait = (ms) => new Promise(res => setTimeout(res, ms));

// Function to convert timestamp to HH:MM:SS format
function convertTimestampToHour(timestamp) {
    const date = new Date(timestamp);
    const hours = ('0' + date.getHours()).slice(-2);
    const minutes = ('0' + date.getMinutes()).slice(-2);
    const seconds = ('0' + date.getSeconds()).slice(-2);
    return `${hours}:${minutes}:${seconds}`;
}

//get WsEndpoint
async function getWsEndpoint() {
    let wsEndpoint = await launch();
    return wsEndpoint;
}

(async () => {
    const browser = await puppeteer.connect({
        browserWSEndpoint: await getWsEndpoint(),
        defaultViewport: null,
    });

    let page = await browser.newPage();
    await page.goto("https://1xbet.com/en/allgamesentrance/crash", { timeout: 60000 });

    const client = await page.target().createCDPSession()

    await client.send('Network.enable')

    let round = 1;
    let roundData = {
        OnStart: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
        OnCashouts: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
        OnCrash: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
        OnBets: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 }
    };

    client.on('Network.webSocketFrameReceived', ({ requestId, timestamp, response }) => {
        let payloadString = response.payloadData.toString('utf8');
        console.log('WebSocket payload received:', payloadString);
        
        try {
            payloadString = payloadString.replace(/[^\x20-\x7E]/g, "");
            const payload = JSON.parse(payloadString);
    
            // Extract data based on event type
            let eventType;
            let eventData;
    
            if (payload.target === 'OnCrash' || payload.target === 'OnStart' || payload.target === 'OnCashouts' || payload.target === 'OnBets') {
                eventType = payload.target;
                eventData = payload.arguments[0];
    
                if (!roundData[eventType]) {
                    roundData[eventType] = { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 };
                }
    
                roundData[eventType].time = convertTimestampToHour(eventData.ts); // Convert timestamp to HH:MM:SS format
                roundData[eventType].numberOfPlayers = eventData.n || 0;
    
                if (eventType === 'OnCashouts') {
                    roundData[eventType].totalWinning = eventData.won || 0;
                } else if (eventType === 'OnBets') {
                    roundData[eventType].totalBet = eventData.bid || 0; // Update total bet amount directly from eventData
                    roundData[eventType].totalWinning = eventData.won || 0; // Update total winning amount directly from eventData
                } else {
                    roundData[eventType].totalBet = eventData.l || 0;
                    roundData[eventType].totalWinning = eventData.f || 0;
                }
    
                if (eventType === 'OnCrash') {
                    // Write data for each round
                    const csvData = `"Round${round}","Time: ${roundData.OnStart.time}","NumberOfPlayers: ${roundData.OnCashouts.numberOfPlayers}","TotalBet: ${roundData.OnBets.totalBet.toFixed(2)}","TotalWinning: ${roundData.OnCashouts.totalWinning}","OnCash: ${roundData.OnCrash.totalWinning}"\n`;
                    
                    fs.appendFile('data.csv', csvData, (err) => {
                        if (err) throw err;
                    });
                    
                    // Reset round data
                    round++;
                    roundData = {
                        OnStart: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
                        OnCashouts: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
                        OnCrash: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 },
                        OnBets: { time: 0, numberOfPlayers: 0, totalBet: 0, totalWinning: 0 }
                    };
                }
                
            }
        } catch (error) {
            console.error('Error processing WebSocket frame:', error);
        }
    });
    

    while(true){
        await page.keyboard.press("Tab");
        await wait(1000);
        await page.keyboard.press("ArrowDown");
        await wait(1000);
    }
})();
