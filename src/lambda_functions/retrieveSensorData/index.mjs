import { TimestreamWrite } from "@aws-sdk/client-timestream-write";

// Main function
export const handler = async (event) => {
    // Create new TimestreamWrite object
    const timestreamWrite = new TimestreamWrite({ region: "us-east-1" });

    let map = create_map();
    
    // JSON received
    let data = event;

    // Unpack JSON
    let pi_id = data.p;
    let temp = data.t;
    let door = data.d;

    // Check for required fields
    if (pi_id === undefined || temp === undefined || door === undefined) {
        console.error("Missing required fields in event:", body);
        return {
            statusCode: 400,
            body: JSON.stringify({ error: "Missing required fields: p, t, d" })
        };
    }
    
    // Get current time in UTC milliseconds
    let utc_time = String(Date.now());

    // Calc  EST time
    let est_time = calculateEST(Number(utc_time));

    // Create record
    let records = prepare_record(utc_time);
    let dimensions = prepare_dimensions(pi_id, map, est_time);
    let measure_1 = prepare_measure("temp", temp);
    let measure_2 = prepare_measure("door_usage", door);

    // Push measure to multi measure record
    records[0].MeasureValues.push(measure_1);
    records[0].MeasureValues.push(measure_2);

    // Parameters for writing to Timestream
    const params = {
        DatabaseName: "RVACF-Timestream-DB",
        TableName: "multi_value",
        Records: records,
        CommonAttributes: dimensions
    };

    // Try writing to Timestream DB
    try {
        await timestreamWrite.writeRecords(params);

        return {
            statusCode: 200,
            body: JSON.stringify({ message: "Data written successfully" })
        };
    } catch (err) {
        console.error("Error writing to Timestream:", err);
        return {
            statusCode: 500,
            body: JSON.stringify({ message: "Error writing to Timestream", error: err.message })
        };
    }
};

// Helper Functions

// Create map for pi ID and fridges
function create_map() {
    let map = new Map([
      [0, "venable-st-fridge"],
      [1, "hull-st-fridge"],
      [2, "new-kingdom-fridge"],
      [3, "oakword-art-fridge"],
      [4, "city-church-fridge"],
      [5, "studio-23-fridge"],
      [6, "fulton-hill-fridge"],
      [7, "cary-st-fridge"],
      [8, "sankofa-fridge"],
      [9, "meadowbridge-fridge"],
      [10, "6pic-fridge"],
      [11, "fonticello-fridge"],
      [12, "matchblox-mutualaid"],
      [13, "main-st-fridge"]
    ]);
    return map;
}

// Calculate EST time from UTC
function calculateEST(utc_time) {
    let date = new Date(utc_time);

    let est_time = date.toLocaleString('en-US', {
        timeZone: 'America/New_York',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });

    return est_time;
}

// Create dimensions for current data insert
function prepare_dimensions(pi_id, map, est_time) {
    return {
        Dimensions: [
            { Name: "region", Value: "us-east-1" },
            { Name: "fridge_id", Value: map.get(pi_id) || "unknown-fridge" },
            { Name: "est_time", Value: est_time}
        ]
    };
}

// Prepare measure for record multi-measure list
function prepare_measure(measure_name, measure_value) {
    return {
        Name: measure_name,
        Value: measure_value.toString(),
        Type: "DOUBLE"
    };
}

// Prepare record to be inserted
function prepare_record(current_time) {
    return [{
        Time: current_time,
        MeasureName: "fridge_metrics",
        MeasureValues: [],
        MeasureValueType: "MULTI"
    }];
}