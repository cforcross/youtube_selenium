import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, smtplib, os, json
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText


load_dotenv()

youtube_trending_url = "https://www.youtube.com/feed/trending"


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    # return driver


def get_videos(driver):
    video_div_tag = "ytd-video-renderer"
    driver.get(youtube_trending_url)
    print(driver.title)
    return driver.find_elements(By.TAG_NAME, video_div_tag)
    # return video


def parse_video(video):
    title_tag = video.find_element(By.ID, "video-title")
    title = title_tag.text

    url = title_tag.get_attribute("href")

    thumbnail_tag = video.find_element(By.TAG_NAME, "img")
    thumbnail_url = thumbnail_tag.get_attribute("src")

    channel_div = video.find_element(By.CLASS_NAME, "ytd-channel-name")
    channel_name = channel_div.text

    channel_views = video.find_element(
        By.CLASS_NAME, "style-scope ytd-video-meta-block"
    )
    channel_views = channel_views.text

    description = video.find_element(By.ID, "description-text").text

    return {
        "title": title,
        "url": url,
        "thumbnail_url": thumbnail_url,
        "channel_name": channel_name,
        # "channel_views": channel_views,
        "description": description,
    }


def send_email(body):
    try:
        server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server_ssl.ehlo()

        SENDER_EMAIL = "bytenull66@gmail.com"
        RECEIVER_EMAIL = "bytenull66@gmail.com"
        SENDER_PASSWORD = "manofsteel"

        subject = "YouTube Trending Videos"

        email_text = f"""
    From: {SENDER_EMAIL}
    To: {RECEIVER_EMAIL}  
    Subject: {subject}
    {body}
    """

        server_ssl.login(SENDER_EMAIL, SENDER_PASSWORD)
        server_ssl.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, email_text)
        server_ssl.close()

    except:
        print("Something went wrong...")


def send_mails():
    # os.getenv
    emailfrom = os.getenv("SENDER_EMAIL")
    emailto = os.getenv("SENDER_EMAIL")
    fileToSend = "trending_videos.csv"
    username = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Subject"] = "help I cannot send an attachment to save my life"
    msg.preamble = "help I cannot send an attachment to save my life"

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend, encoding="utf8")
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(fileToSend, "rb", encoding="utf8")
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(fileToSend, "rb", encoding="utf8")
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb", encoding="utf8")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username, password)
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()


if __name__ == "__main__":
    print("Creating driver")
    driver = get_driver()

    print("Fetching trending videos")
    videos = get_videos(driver)

    print(f"Found {len(videos)} videos")

    print("Parsing top 10 videos")
    videos_data = [parse_video(video) for video in videos[:10]]

    print("Save the data to a CSV")
    videos_df = pd.DataFrame(videos_data)
    videos_df.to_csv("trending.csv", index=None)

    print("Sending the results over email")
    # body = json.dumps(videos_data, indent=2)
    # send_emails(body)
    send_mails()

    print("Finished.")
