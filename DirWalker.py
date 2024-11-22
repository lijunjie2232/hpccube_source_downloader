import requests
import json
import pandas as pd
from File import File
from Downloader import Downloader
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import ssl
import warnings

warnings.filterwarnings("ignore")

ssl._create_default_https_context = ssl._create_unverified_context
VERIFY_SSL = False

domain = "https://cancon.hpccube.com:65024"
route_driver_info = "/api/drive/list"
route_list_api = "/api/list/%d"

list_data = {
    "path": "/",
    "password": "",
    "orderBy": "",
    "orderDirection": "",
}
_SESSION = requests.session()
_DOWNLOADER = Downloader(_SESSION, verify_ssl=VERIFY_SSL)
_SAVE_DIR = "/public/home/lijunjie/dev_source/%s"

_THREAD_POOL = None

def driverWalker(multi_thread=False):
    resp = json.loads(_SESSION.request(
        url=domain+route_driver_info,
        method="get",
        verify=VERIFY_SSL
    ).text)
    assert resp["code"] == 0, resp["msg"]
    driver_list = pd.DataFrame(resp["data"]["driveList"])
    driver_loop = tqdm(driver_list.iterrows(), colour="#74b9ff", total=driver_list.shape[0])
    for _, row in driver_loop:
        driver_id = row["id"]
        driver_name = row["name"]
        driver_loop.set_postfix_str(driver_name)
        main_url = domain + route_list_api%driver_id
        save_dir = (_SAVE_DIR%driver_name).replace(" ", "_")
        rootDir = File(
                {
                    'name': "",
                    'time': None,
                    'size': 0,
                    'type': "FOLDER",
                    'path': "/",
                    'url': None,
                }
            )
        rootDir.isDir()
        if multi_thread:
            _THREAD_POOL.submit(dirWalker, rootDir, main_url, save_dir=save_dir)
        else:
            dirWalker(rootDir, main_url, save_dir=save_dir)


def dirWalker(dir:File, main_url, save_dir:str, recycle=True, leave=False):
    dir_path = os.path.join(dir.get("path"), dir.get("name"))
    req_data = list_data.copy()
    req_data["path"] = dir_path
    resp = json.loads(_SESSION.request(
        url=main_url,
        method="get",
        params=req_data,
        verify=VERIFY_SSL
    ).text)
    assert resp["code"] == 0, resp["msg"]
    
    floop = tqdm(resp["data"]["files"], desc=dir_path, leave=leave)
    for i in floop:
        file = File(i)
        floop.set_postfix_str(file.get("name"))
        if file.isDir() and recycle:
            # print("dir:", file.get("path"), file.get("name"))
            dirWalker(file, main_url, save_dir)
        else:
            pass
            # print("file:", file.get("path"), file.get("name"))
            # print(file.get("path"), file.get("name"))
            _DOWNLOADER.Download(file, saveDir=save_dir)


if __name__ == '__main__':
    _THREAD_POOL = ThreadPoolExecutor(max_workers=2)
    driverWalker(multi_thread=False)
    _THREAD_POOL.shutdown()

