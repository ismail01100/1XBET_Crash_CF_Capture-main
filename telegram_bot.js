// telegram_bot.js

const fs = require('fs');
const { Telegraf } = require('telegraf');
const { PythonShell } = require('python-shell');

// Create a new Telegram bot instance
const bot = new Telegraf('7162902135:AAGJsFExgyixhXGk-eg1Tj3TnZiQu4L1D8Q');

// Load the trained prediction model
const model = 'crash_prediction_model.joblib';

// Function to preprocess the latest round data
function preprocessData(roundData) {
    // Perform any preprocessing steps here if needed
    return roundData;
}

// Command handler to predict the next round's OnCrash value
bot.command('predict', async (ctx) => {
    // Read the latest round data from data.csv
    const latestRoundData = fs.readFileSync('data.csv', 'utf8').trim().split('\n').pop();

    // Parse the latest round data
    const latestRoundValues = latestRoundData.split('\t');
    const latestRoundObject = {
        NumberOfPlayers: parseFloat(latestRoundValues[1].split(':')[1].trim()),
        TotalBet: parseFloat(latestRoundValues[2].split(':')[1].trim()),
        TotalWinning: parseFloat(latestRoundValues[3].split(':')[1].trim()),
        OnCash: parseFloat(latestRoundValues[4].split(':')[1].trim())
    };

    // Preprocess the latest round data
    const preprocessedData = preprocessData(latestRoundObject);

    // Call the Python script to make predictions
    PythonShell.run('prediction_model.py', null, (err, result) => {
        if (err) {
            console.error(err);
            ctx.reply('An error occurred while predicting the next OnCrash value.');
        } else {
            // Extract the predicted value from the result
            const predictedOnCrash = parseFloat(result[result.length - 1]);

            // Send the predicted value as a message to the user
            ctx.reply(`Predicted OnCrash value for the next round: ${predictedOnCrash}`);
        }
    });
});

// Start the bot
bot.launch();
