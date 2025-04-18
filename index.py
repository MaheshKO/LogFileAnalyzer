import re
import json
from collections import Counter
from datetime import datetime
import logging

logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def parseLogLine(line):
    pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - ([^-]+) - ([A-Z]+) - (.+)$'
    match = re.match(pattern, line.strip())
    if match:
        timestampStr, service, level, message = match.groups()
        try:
            timestamp = datetime.strptime(timestampStr, "%Y-%m-%d %H:%M:%S")
            return {
                'timestamp': timestamp,
                'serviceName': service.strip(),
                'logLevel': level.strip(),
                'message': message.strip()
            }
        except ValueError:
            logging.warning(f"Invalid timestamp format: {line.strip()}")
            return None
    else:
        logging.warning(f"Malformed log line: {line.strip()}")
        return None

def readLogFile(filePath):
    entries = []
    with open(filePath, 'r') as f:
        for line in f:
            parsed = parseLogLine(line)
            if parsed:
                entries.append(parsed)
    return entries

def analyzeLogs(entries):
    levelCounter = Counter()
    serviceCounter = Counter()
    errorMessages = Counter()

    for entry in entries:
        level = entry['logLevel']
        service = entry['serviceName']
        message = entry['message']

        levelCounter[level] += 1
        serviceCounter[service] += 1

        if level == 'ERROR':
            errorMessages[message] += 1

    mostCommonError = errorMessages.most_common(1)
    commonError = {
        'message': mostCommonError[0][0],
        'count': mostCommonError[0][1]
    } if mostCommonError else {}

    return {
        'logLevels': dict(levelCounter),
        'services': dict(serviceCounter),
        'mostCommonError': commonError
    }

def filterLogsByTime(entries, startTime, endTime):
    return [entry for entry in entries if startTime <= entry['timestamp'] <= endTime]

def printSummary(summary):
    print(json.dumps(summary, indent=4, default=str))

def main():
    logFile = "app.log"
    entries = readLogFile(logFile)
    summary = analyzeLogs(entries)
    printSummary(summary)

if __name__ == "__main__":
    main()
