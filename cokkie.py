from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
import json

# Đường dẫn đến Edge WebDriver
edge_driver_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"


# Tạo tùy chọn trình duyệt Edge
edge_options = Options()
edge_options.add_argument('--start-maximized')

# Khởi tạo WebDriver cho Edge
service = EdgeService(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service, options=edge_options)

# Điều hướng đến URL
url = 'https://vtvgo.vn/xem-truc-tuyen-kenh-vtv1-1.html'
driver.get(url)

# Lấy cookie
cookies = driver.get_cookies()

# Lưu cookie vào file
with open('cookies_edge.json', 'w') as f:
    json.dump(cookies, f, indent=4)

# In ra cookie
for cookie in cookies:
    print(f'{cookie["name"]}: {cookie["value"]}')

# Đóng trình duyệt
driver.quit()
