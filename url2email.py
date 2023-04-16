import re
import urllib.request
import datetime
import threading
import queue
import time
from tqdm import tqdm
# Prompt the user to enter the file path of the URLs file
file_path = input('Enter the file path of the URLs file: ')
# Prompt the user to enter the timeout (in seconds)
timeout = int(input('Enter the timeout (in seconds): '))
# Prompt the user to enter the scraping timeout (in seconds)
scraping_timeout = int(input('Enter the scraping timeout (in seconds): '))
# Prompt the user to choose whether to follow redirects or not
# Prompt the user to enter the number of threads
num_threads = int(input('Enter the number of threads: '))
# Define the regex pattern for email addresses
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
# Create a queue to store the URLs
url_queue = queue.Queue()
# Open the file containing the URLs and add each URL to the queue
with open(file_path, 'r') as urls_file:
    for url in urls_file:
        # Add "http://" in front of the URL if it doesn't start with "http"
        url = url.strip()
        if not url.startswith("http"):
            url = "http://" + url
        url_queue.put(url)
# Define a function to scrape emails from a URL
def scrape_emails_from_url(progress_bar):
    while True:
        try:
            # Retrieve the next URL from the queue
            url = url_queue.get_nowait()
        except queue.Empty:
            # If the queue is empty, exit the thread
            break  
        # Retrieve the HTML content of the webpage
        try:
            response = urllib.request.urlopen(url, timeout=timeout)
            html_content = response.read().decode('utf-8', 'ignore')
        except urllib.error.URLError as e:
            print(f"An error occurred while retrieving {url}: {e.reason}")
            continue  # Skip if there is an error retrieving the content   
        # Extract email addresses using regex
        extracted_emails = re.findall(email_pattern, html_content)
        # Print the current URL and number of scraped emails
        with threading.Lock():
            progress_bar.update(1)
        # Write the extracted emails to the output file
        with open('output.txt', 'a') as output_file:
            for email in extracted_emails:
                output_file.write(email + '\n')
        # Mark the task as done in the queue
        url_queue.task_done()
        # Wait for the specified scraping timeout
        time.sleep(scraping_timeout)
# Create a list to store the threads
threads = []
# Initialize the progress bar
num_urls = url_queue.qsize()
progress_bar = tqdm(total=num_urls, desc='Scraping URLs')
# Start the threads
for i in range(num_threads):
    thread = threading.Thread(target=scrape_emails_from_url, args=(progress_bar,))
    thread.start()
    threads.append(thread)
# Wait for all tasks in the queue to be processed
url_queue.join()
# Stop the threads
for thread in threads:
    thread.join()
# Close the progress bar
# Create a list to store the threads
threads = []
# Initialize the progress bar
num_urls = url_queue.qsize()
progress_bar = tqdm(total=num_urls, desc='Scraping URLs')
# Generate the filename based on the current date
filename = 'file' + datetime.datetime.now().strftime('%Y-%m-%d') + '.txt'
# Open the output file in append mode
output_file = open(filename, 'a')
# Start the threads
for i in range(num_threads):
    thread = threading.Thread(target=scrape_emails_from_url, args=(progress_bar,))
    thread.start()
    threads.append(thread)
# Wait for all tasks in the queue to be processed
url_queue.join()
# Stop the threads
for thread in threads:
    thread.join()
# Close the progress bar
progress_bar.close()
# Close the output file
output_file.close()
# Print a message to inform the user that the extraction is complete
print('Emails have been extracted and saved to', filename + '.')
