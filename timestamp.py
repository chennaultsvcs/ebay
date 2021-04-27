import datetime

def timeStamp(string, source):
	timeStamp = datetime.datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
	print(f'[{timeStamp}] [{source}] {string}')

if __name__ == "__main__":
	timeStamp(string)
