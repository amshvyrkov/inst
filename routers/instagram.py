from typing import List
import asyncio
from fastapi import APIRouter, UploadFile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

router = APIRouter()


async def get_photos_async(username: str, max_count: int):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    profile_url = f"https://www.instagram.com/{username}/"
    driver.get(profile_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "img"))
    )
    photo_elements = driver.find_elements(By.TAG_NAME, "img")
    photo_urls = [elem.get_attribute("src") for elem in photo_elements]

    driver.quit()
    return {"urls": photo_urls}


async def post_photos_async(photos: List[UploadFile], caption: str):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    post_url = "https://www.instagram.com/create/upload"
    driver.get(post_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "input"))
    )
    input_elements = driver.find_elements(By.TAG_NAME, "input")
    for i, photo in enumerate(photos):
        input_elements[i].send_keys(photo.file)
    caption_element = driver.find_element(By.TAG_NAME, "textarea")
    caption_element.send_keys(caption)
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit_button.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/p/')]"))
    )
    post_link = driver.find_element(By.XPATH, "//a[contains(@href, '/p/')]").get_attribute("href")
    driver.quit()
    return {"postURL": post_link}


@router.get("/getPhotos")
async def get_photos(username: str, max_count: int):
    loop = asyncio.get_event_loop()
    tasks = [get_photos_async(username, max_count) for _ in range(3)]
    results = await asyncio.gather(*tasks)
    return results


@router.post("/postPhotos")
async def post_photos(photos: List[UploadFile], caption: str):
    loop = asyncio.get_event_loop()
    tasks = [post_photos_async(photos, caption) for _ in range(3)]
    results = await asyncio.gather(*tasks)
    return results
