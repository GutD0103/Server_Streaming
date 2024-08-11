#pip install undetected-chromedriver
import undetected_chromedriver as uc 
import time

# Initializing driver 
def get_cookie(url, name):
    # headless flag must be fail
    driver = uc.Chrome(headless=False,use_subprocess=True) 
    driver.get(url)
    time.sleep(1)
    my_cookie = driver.get_cookie(name)
    print (my_cookie)
    driver.close()
    # very importance if remove will raise an error
    time.sleep(1)
    return my_cookie.get("value") 

if __name__ == "__main__" :
    # print(get_cookie("https://vtvgo.vn/xem-truc-tuyen-kenh-vtv3-3.html","aws-waf-token"))
    print(get_cookie("https://vtvgo.vn/xem-truc-tuyen-kenh-vtv1-1.html","aws-waf-token"))
    
    
