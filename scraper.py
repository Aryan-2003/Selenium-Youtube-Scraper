from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import os
# import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

YOUTUBE_TRENDING_URL='https://www.youtube.com/feed/trending'

def get_driver():
  chrome_options = Options() 
  chrome_options.add_argument('--no-sandbox') 
  chrome_options.add_argument("--disable-dev-shm-usage");
  chrome_options.add_argument('headless')
  driver=webdriver.Chrome(options=chrome_options)
  return driver

def get_videos(driver):
  VIDEO_DIV_TAG='ytd-video-renderer'
  driver.get(YOUTUBE_TRENDING_URL)
  videos=driver.find_elements(By.TAG_NAME,VIDEO_DIV_TAG)
  return videos


def parse_video(video):
  title_tag=video.find_element(By.ID,'video-title')
  title=title_tag.text
  url=title_tag.get_attribute('href')

  thumbnail_tag=video.find_element(By.TAG_NAME,'img')
  thumbnail_url=thumbnail_tag.get_attribute('src')

  channel_div=video.find_element(By.CLASS_NAME,'ytd-channel-name')
  channel_name=channel_div.text

  description=video.find_element(By.ID,'description-text').text

  channel_views_uploaded_div=video.find_element(By.CLASS_NAME,'ytd-video-meta-block')
  channel_views_uploaded_str=channel_views_uploaded_div.text
  channel_views_uploaded_lst=channel_views_uploaded_str.split('\n')
  views=channel_views_uploaded_lst[1]
  uploaded=channel_views_uploaded_lst[2]

  return {
    'title':title,
    'url':url,
    'thumbnail_url':thumbnail_url,
    'channel':channel_name,
    'description':description,
    'views':views,
    'uploaded':uploaded
  }

def send_email(body):
  
  try:
    server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server_ssl.ehlo()  

    SENDER_EMAIL='latesttrendstop10@gmail.com'
    RECEIVER_EMAIL='latesttrendstop10@gmail.com'
    SENDER_PASSWORD=os.environ['GMAIL_PASSWORD']
    subject = 'Youtube Trendng Videos'

    email_text = f"""
    From: {SENDER_EMAIL}
    To: {RECEIVER_EMAIL}
    Subject: {subject}
    {body}
    """ 

    server_ssl.login(SENDER_EMAIL,SENDER_PASSWORD)
    server_ssl.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, email_text)
    server_ssl.close()

  except:
    print('Something went wrong...')


def send_attachment(file):
  try:
    SENDER_EMAIL = "latesttrendstop10@gmail.com"
    RECEIVER_EMAIL = "latesttrendstop10@gmail.com"
    SENDER_PASSWORD=os.environ['GMAIL_PASSWORD']
      
    # instance of MIMEMultipart
    msg = MIMEMultipart()
      
    # storing the senders email address  
    msg['From'] = SENDER_EMAIL
      
    # storing the receivers email address 
    msg['To'] = RECEIVER_EMAIL
      
    # storing the subject 
    msg['Subject'] = "YouTube Trending Videos"
      
    # string to store the body of the mail
    body = "Check out the top 10 trending videos on Youtube today."
      
    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
      
    # open the file to be sent 
    filename = file
    attachment = open(file, "rb")
      
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
      
    # To change the payload into encoded form
    p.set_payload((attachment).read())
      
    # encode into base64
    encoders.encode_base64(p)
      
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
      
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)
      
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
      
    # start TLS for security
    s.starttls()
      
    # Authentication
    s.login(SENDER_EMAIL, SENDER_PASSWORD)
      
    # Converts the Multipart msg into a string
    text = msg.as_string()
      
    # sending the mail
    s.sendmail(SENDER_EMAIL,RECEIVER_EMAIL,text)
      
    # terminating the session
    s.quit()
  
  except:
    print('Something went wrong..')

if __name__=='__main__':
  print('Creating driver...')
  driver=get_driver()

  print('Fetching trending videos...')
  videos=get_videos(driver)
  print(f"Found {len(videos)} videos")

  print('Parsing top 10 videos...')

  videos_data=[parse_video(video) for video in videos[:10]]
  # print(videos_data)
  
  print('Save the data to a csv file')
  videos_df=pd.DataFrame(videos_data)

  # print(videos_df)
  videos_df.to_csv('trending.csv',index=None)

  print('Send the results over Email')
  # body=json.dumps(videos_data,indent=2)
  # send_email(body)
  send_attachment('trending.csv')
  print('Finished.')



