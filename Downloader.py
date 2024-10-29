import requests
import os
from File import File
import threading
from tqdm import tqdm
import traceback
import sys


class Downloader(threading.Thread):
    _DOWNLOAD_CHUNK_SIZE = 8388608  # 8 MB

    def __init__(
        self,
        session: requests.Session,
        verify_ssl = True
    ):
        self._session = session
        self.downloadHeaders = {
            "Accept-Ranges": "bytes",
            "Range": "bytes=0-",
        }
        self.VERIFY_SSL = verify_ssl

    def refreshRange(self, start: int = 0):
        self.downloadHeaders["Range"] = "bytes=%d-" % start

    def Download(
        self,
        file: File,
        saveDir: str = "./downloads",
        keepOriginStructure: bool = True,
        overwrite=False,
        showProgress=True,
        single=False,
    ) -> str:
        """_summary_

        Args:
            file : GridviewFile オブジエクトである
            savePath (str, optional): ファイルの出力するパス
            keepOriginStructure (bool, optional): 元の相対位置を維持するかどうか Defaults to True.
            overwrite (bool, optional): 同じ名前のファイルを上書きするかどうか Defaults to False.

        Returns:
            str: ファイルの出力するパス
        """
        filePath = file.get("path")
        saveName = file.get("name")

        assert not os.path.isfile(saveDir), 'saveDirはファイルで入力することができません'
        saveDir = os.path.join(saveDir, filePath[1:])
        savePath = os.path.join(saveDir, saveName)
        os.makedirs(saveDir, exist_ok=True)


        tmpPath = savePath + ".tmp"
        tmpSize = 0
        if os.path.exists(savePath):
                return
        elif os.path.exists(tmpPath):
            tmpSize = os.path.getsize(tmpPath)
        self.refreshRange(start=tmpSize)

        self._session.headers.update(self.downloadHeaders)
        try:
            progress_bar = None
            # noinspection PyProtectedMember
            with self._session.request(
                method="get",
                url=file.get("url"),
                stream=True,
                verify=self.VERIFY_SSL
            ) as resp:
                llen = int(resp.headers.get("content-length", 0))
                if resp.headers.get("Accept-Ranges", None) != "bytes":
                    raise ValueError(f'リンク"{resp.url}"が期限切れました')
                if showProgress:
                    progress_bar = tqdm(
                        total=llen+tmpSize,
                        unit="B",
                        unit_scale=True,
                        colour="#fd79a8",
                        desc=file.get("name"),
                        leave=single
                    )
                    progress_bar.update(tmpSize)
                with open(tmpPath, "ab") as f:
                    for content in resp.iter_content(
                        chunk_size=self._DOWNLOAD_CHUNK_SIZE
                    ):
                        if showProgress:
                            progress_bar.update(len(content))
                        f.write(content)
                        f.flush()
            assert os.path.getsize(tmpPath) == file.get("size"), "size not fit"
            os.rename(tmpPath, savePath)
        except Exception as e:
            print(sys.exc_info()) 
            print('\n'+'>>>' * 20)
            print(traceback.print_exc())
            print('\n'+'>>>' * 20)
            #pass
            


        finally:
            if progress_bar:
                progress_bar.close()
        # print("ファイルはダウンロードすることがしまいました")
        return filePath
