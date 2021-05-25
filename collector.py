from perceval.backends.core.slack import Slack
import datetime
import re
import argparse
import sys

"""
  This function parses command line arguments
"""
def parse_arguments(cmd_args):
  def valid_date(s):
    try:
      return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
      msg = "Not a valid date: '{0}'.".format(s)
      raise argparse.ArgumentTypeError(msg)

  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--output', dest='filename')
  parser.add_argument('-c', '--channel', dest='channel', required=True)
  parser.add_argument('-t', dest='slack_token', required=True)
  parser.add_argument('--from-date', dest='from_date', help="Start collecting from: YYYY-MM-DD HH:MM:SS",type=valid_date)
  args = parser.parse_args(cmd_args)
  return args

"""
  This function fetches slack information and parses it
"""
def fetch_slack_information(args):
    slack_token = args.slack_token
    channel = args.channel

    from_date = None
    if args.from_date:
        from_date = args.from_date

    slack = Slack(channel=channel, api_token=slack_token)
    data = slack.fetch(from_date=from_date)

    metadata = None
    participants = {}
    messages = []

    while True:
        try:
            record = next(data)
            record_data = record.get('data',None)
            if record_data:
                timestamp = int(record_data.get('ts').split('.')[0])
                utc_time = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
                message = record_data.get('text')
                user_data = record_data.get('user_data', None)
                if user_data:
                    username = user_data.get('profile')['display_name']
                    user_id = user_data.get('id')
                    participants[user_id] = username
                    messages.append('{} - {}: {}'.format(utc_time,username,message))
                if not metadata:
                    metadata = {}
                    metadata['channel_name'] =  record_data.get('channel_info')['name']
        except StopIteration:
            break

    return messages, participants, metadata


"""
  This function writes logs to an output file.
"""
def write_log_file(messages, participants, metadata):
    print('Writing log file...')
    if args.filename:
      filename = args.filename
    else:
      filename = "slack-logs.txt"

    textfile = open(filename, "w")

    def replacer(obj):
        return '@' + participants[obj.group(0)[2:-1]]

    textfile.write("Channel name: " + metadata['channel_name'] + '\n')
    textfile.write("Participants: " + ', '.join(participants.values()))
    textfile.write(
      '\n________________________________________________________________________________________________\n')
    for message in reversed(messages):
        enriched_message = re.sub(r"<@[A-Z0-9]+>+", replacer, message)
        textfile.write(enriched_message + "\n")
    textfile.close()
    print('Logs written to {}'.format(filename))


if __name__ == "__main__":
    args = parse_arguments(sys.argv[1:])

    messages, participants, metadata = fetch_slack_information(args)
    if messages:
        write_log_file(messages, participants,metadata)
    else:
        print("No logs found. Exiting...")

