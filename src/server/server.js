import express from 'express';
import bodyParser from 'body-parser';
import db from './db.js';

const app = express();
const port = 3000;

app.use(bodyParser.json());

app.post('/api/fridgedata', (req, res) => {
  let data = JSON.stringify(req.body);
  console.log(`Recieved Data:\n${data}`);
  // DATA PROCESSING GOES HERE

  // END DATA PROCESSING
  res.send("Recieved!\n");
});

app.get('/test_database', async (req, res) => {
    const dbRes = await db.query(
        'SELECT f.location FROM refridgerator as f' 
    )
    //Output fridges from database in an html unorder list
    res.send('<ul>' + dbRes.rows.map(instance => 'Fridge: ' + instance['location']).join('<br>') + '</ul>');
});

app.listen(process.env.PORT || port, () => {
  console.log(`Server is running on port ${port}`);
});
