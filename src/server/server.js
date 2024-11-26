import express from 'express';
import bodyParser from 'body-parser';

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

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});