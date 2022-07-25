import time
import requests
print("Enter link:")
link = input() + "/dell_time_it_up_image"

while True:
    requests.get(link)
    time.sleep(3600)