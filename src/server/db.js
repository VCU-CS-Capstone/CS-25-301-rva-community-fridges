import * as dotenv from 'dotenv';
dotenv.config({path:'../../.env'});

import postgres from 'pg';
const {Pool} = postgres;

//CONNECTION INFORMATION FOR POSTGRES
const pool = new Pool({
	user:process.env.user,
	password:process.env.password,
	host:process.env.host,
	port:process.env.port,
	database:process.env.dbname
})

async function connect_to_db(){
	try {
		const client = await pool.connect()
		console.log("Connected to RVACF database")
		client.release()
	}
	catch(error){
		console.log("Could not connect to RVACF database \n")
        console.log(error)
	}
}
//TEST CONNECTION TO DATABASE
connect_to_db()

//QUERY FUNCTION FOR DATABASE ACCESS
export default { 
	query: (text, parameters) => pool.query(text, parameters)
}

