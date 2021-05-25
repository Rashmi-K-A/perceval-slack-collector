## Perceval Slack Logs Collector

This log collector is to collect slack messages from a channel using perceval.

### Usage:
1. Install dependencies in `requirements.txt`.
2. Run the following command:
```
python3 collector.py -t <SLACKTOKEN> -c C000000001 --from-date "2021-05-24 13:30:00"
```
**Note:** Specify the time for from-date argument in UTC

### Additional links
https://github.com/chaoss/grimoirelab-perceval#slack
