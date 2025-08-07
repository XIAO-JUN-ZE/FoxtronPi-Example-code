# FoxtronPi-Example-code

這是 FoxtronPi Example code，使用 Python 撰寫 Read、Write DID 功能，並透過 UDS / DOIP 與FD進行通訊。

## 📁 專案內容

| 檔案名稱       | 功能簡介                     |
|----------------|------------------------------|
| `FoxPi_read.py`  | 讀取車輛訊號狀態（如車速、車燈、電池、馬達等） |
| `FoxPi_write.py` | 控制車輛訊號（如加減速度、目標車速、開啟燈光、變換檔位等）    |
| `README.md`     | 本說明文件                  |
| `Linux_require.txt` | Ubuntu 需求套件 |
| `Windows_require.txt` | Windows 需求套件 |

---

## 🚀 安裝方式

1. 複製(clone)本專案：
```bash
git clone git@github.com:XIAO-JUN-ZE/FoxtronPi-Example-code.git
```
2. 進入資料夾後安裝需求套件:
```bash
cd FoxtronPi-Example-code
```
### Ubuntu 需求套件
```bash
pip install -r Linux_require.txt
```
### Windows 需求套件 
```bash
pip install -r Windows_require.txt
```

## 🧪 執行方式
1. **Read DID**
```bash
python3 FoxPi_read.py
```
2. **Write DID**
```bash
python3 Foxpi_read.py
```

