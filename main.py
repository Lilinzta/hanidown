import asyncio
import os
import re
from bilix.sites.hanime1 import DownloaderHanime1
from bs4 import BeautifulSoup
from selenium import webdriver


def init_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options)
    return driver


def main():
    driver = init_driver()
    driver.get("https://hanime1.me/playlist?list=xxx")
    page_source = driver.page_source
    playlist_videos_id = list(
        set(re.findall(r"https://hanime1\.me/watch\?v=([\w-]+)", page_source))
    )
    soup = BeautifulSoup(page_source, "html.parser")
    playlist_name = (
        soup.find("title")
        .text.strip()
        .replace("-\u00a0H\u52d5\u6f2b/\u88cf\u756a/\u7dda\u4e0a\u770b\u00a0", "")
    )
    driver.quit()
    for series_video_id in playlist_videos_id:
        driver = init_driver()
        driver.get("https://hanime1.me/watch?v=" + series_video_id)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        video_artist = soup.find(id="video-artist-name").contents[0].strip()
        video_name = (
            soup.find("title")
            .text.strip()
            .replace("-\u00a0H\u52d5\u6f2b/\u88cf\u756a/\u7dda\u4e0a\u770b\u00a0", "")
        )
        playlist_scroll = soup.find(id="playlist-scroll").contents
        soup = BeautifulSoup(str(playlist_scroll), "html.parser")
        series_videos_id = list(
            set(re.findall(r"https://hanime1\.me/watch\?v=([\w-]+)", str(soup)))
        )
        dir = os.path.join("playlists", playlist_name, video_artist, video_name)
        os.makedirs(dir, exist_ok=True)
        driver.quit()
        asyncio.run(dl_series_video(series_videos_id, dir))


async def dl_series_video(series_videos_id, dir):
    async with DownloaderHanime1() as d:
        for video_id in series_videos_id:
            await d.get_video("https://hanime1.me/watch?v=" + video_id, dir)


if __name__ == "__main__":
    main()
