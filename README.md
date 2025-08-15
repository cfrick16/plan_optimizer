# Plan Optimizer

A FastAPI application that analyzes electricity consumption data and recommends the most cost-effective tariff plan.

## Quick Start

1. Install dependencies:
```
pip install fastapi uvicorn pydantic python-multipart
```

2. Start the server:
```
uvicorn main:app --reload
```

3. Test with sample data:
```
curl -X POST "http://127.0.0.1:8000/recommend_plan"  -F "file=@sample_interval_data/high-winter-interval-data.csv" | jq
```

## API Usage

**Endpoint**: `POST /recommend_plan`

**Input**: CSV file with columns: `datetime`, `duration`, `consumption`, `generation`
- Note: Unit is assumed to always be Wh

**Output**: JSON array of tariff recommendations sorted by cost
- The top tariff can be considered the "winner", all other tariffs are provided to provide the client options.

## Sample Data

Sample test files available in `sample_interval_data/*`


## Implementation notes
If I had more time I would...
- Add detailed unit tests
- Use a more comprehensive framework like Django rather than fastAPI
- Add support for different units
- Provide better error handling
- Create a dedicated tariff_config service that handles the creation and edits of the tariff_config from a central service. This service uses incremental ids for tariff_configs, these should probably be UUIDs managed by another service.
