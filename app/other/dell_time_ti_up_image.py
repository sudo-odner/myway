import time
import requests
print("Enter link:")
link = input() + "/dell-time-it-up-image"

while True:
    requests.get(link)
    time.sleep(3600)