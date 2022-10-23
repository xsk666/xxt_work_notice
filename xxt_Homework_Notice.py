# %%
import time
from pyquery import PyQuery as pq
import requests
import json
req = requests.Session()
req.headers = {
    "Accept-Encoding": "gzip",
    "Accept-Language": "zh-Hans-CN;q=1, zh-Hant-CN;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 com.ssreader.ChaoXingStudy/ChaoXingStudy_3_4.8_ios_phone_202012052220_56 (@Kalimdor)_12787186548451577248"
}

def get_course():
    # 获取课程列表
    res2 = req.get("https://mooc1-2.chaoxing.com/course/phone/courselistdata?courseFolderId=0&isFiled=0&query=")
    doc = pq(res2.text)
    for i in doc('li').items():
        print(json.dumps({
            "courseid":i.attr("courseid"),
            "clazzid":i.attr("clazzid"),
            "classname":i("dt").text()
        },ensure_ascii=False))
    exit()


# 考试提醒
def get_exam():
    global alltaskinfo
    txt="还有学习通的考试哦\n"
    res2=req.get("https://mooc1-api.chaoxing.com/exam/phone/examcode")
    doc2=pq(res2.text)
    num=0
    # 未结束的考试含有dd时间标签
    for i in doc2("li:has(dd)").items():
        data=i.text().split("\n")
        if data[2]=="未交":
            txt+="\n"+data[0]+" "+data[1]
            num+=1
    if num == 0:
        print("暂无考试")
    else:
        print("未考试数量：", num)
        print(txt) 
        alltaskinfo+="\n"+txt


# 获取作业详情
def get_homework(user):
    global alltaskinfo
    txt=""
    num = 0
    print("开始查询")
    for classitem in user["classinfo"]:
        classname = classitem['classname']
        try:
            res3 = req.get(
                f"https://mooc1.chaoxing.com/work/task-list?courseId={classitem['courseid']}&classId={classitem['clazzid']}&vx=1")
            doc2 = pq(res3.text)
            # 未交且作业未截至的作业有两个span，一个是未交，一个是截止时间(含fr类名)
            for task in doc2('li .fr').items():
                if task.siblings("span").text() != "未交":
                    continue
                taskname=task.siblings("p").text()
                txt += f"\n{classname} :{taskname}\n  - {task.text()}"
                num += 1
        except:
            alltaskinfo += f"{classname} 查询失败\n"
            print(classname, "查询失败")
        time.sleep(1)
    if num == 0:
        print("暂无作业\n")
        alltaskinfo=""
    else:
        print("未交作业数量：", num)
        print(txt) 
        alltaskinfo+="学习通作业别忘了哦\n" + txt
                    
if __name__ == "__main__":
    try:
        userdata = json.load(open("./data.json", 'r', encoding='utf8'))
        for user in userdata:
            alltaskinfo = "" 
            req.headers["Cookie"]=""
            account = user["account"]
            password = user["password"]
            url = f"https://passport2-api.chaoxing.com/v11/loginregister?code={password}&cx_xxt_passport=json&uname={account}&loginType=1&roleSelect=true"
            res = req.get(url)
            if res.json().get('status',False):
                # 获取Cookie
                cookie = requests.utils.dict_from_cookiejar(req.cookies)
                mycookie = ""
                for key, value in cookie.items():
                    mycookie += f"{key}={value};"
                req.headers["Cookie"] = mycookie
                print(account,"登录成功")
                # 获取课程信息
                # get_course()
                # 获取作业信息
                get_homework(user)
                # 获取考试信息
                get_exam()                
                print("查询完成:",alltaskinfo)
                # try:
                #     requests.get(
                #         "http://127.0.0.1:8082/send_private_msg?user_id="+user["qq"]+"&message=学习通作业别忘了哦"+alltaskinfo)
                #     print("发送通知成功")
                # except:
                #     print("发送通知失败")
            else:
                print(account,"登录失败")
    except Exception as e:
        print("登陆失败", e)
