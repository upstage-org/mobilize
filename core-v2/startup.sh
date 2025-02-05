#!/bin/sh
# Get the current date in the format DayOfWeek_Day_Month_Year
formatted_date=$(date +"%d_%m_%Y")

# Print the formatted date
echo "Formatted Date: $formatted_date"

# Rename a file to formatted_date.py
if [ -f src/global_config/config_formatted_date.py ]; then
    cp src/global_config/config_formatted_date.py src/global_config/config_$formatted_date.py
else
    echo "Source file does not exist."
fi

# Export the timestamp as an environment variable
export TIMESTAMP=$formatted_date

alembic upgrade head
ruff format src
uvicorn src.main:app --proxy-headers --forwarded-allow-ips='*' --host 0.0.0.0 --port 3000 --reload