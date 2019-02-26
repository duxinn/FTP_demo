from socket import *
import os
from threading import Thread
from tkinter import *
import time
from client_Gui import *
from multiprocessing import Process, Value
import tkinter.filedialog
import tkinter.messagebox


class chuli:
    @classmethod
    # 用户登录函数
    def land_client(self, n, var, pwd, t, connfd, obj):
        name = str(n.get())
        passwd = str(pwd.get())
        if not name:
            print("姓名不合法,请重新输入")
            return
        S = "登录" + "," + name + "," + passwd
        connfd.send(S.encode())
        data = connfd.recv(1024).decode()
        if data == "登录成功":
            print("登录成功")
            obj.state = 1
            t.destroy()
            return
        elif data == "用户名或密码错误":
            print("用户名或密码错误")
            var.set("用户名或密码错误")
            return
        elif data == "用户名不存在,请注册后登录":
            print("用户名不存在,请注册后登录")
            var.set("用户名不存在,请注册后登录")
            return

    @classmethod
    # 客户端注册函数
    def usrsign(self, var, ns, pwds, pwds1, t, connfd):
        names = str(ns.get())
        passwds = str(pwds.get())
        passwds1 = str(pwds1.get())

        if not names:
            print("姓名不合法,请重新输入")
            var.set('姓名不合法,请重新输入')
            return
        if passwds != passwds1:
            print("输入的两次密码不一致，请重新输入")
            var.set('输入的两次密码不一致，请重新输入')
            return
        S = "注册" + "," + names + "," + passwds
        connfd.send(S.encode())
        data = connfd.recv(1024).decode()
        if data == "注册成功":
            print("注册成功")
            var.set('注册成功')
            t.destroy()
            return
        elif data == "用户名已被占用":
            print("用户名已被占用")
            var.set('用户名已被占用')
        return

    @classmethod
    # 客户端接收消息函数-暂时没有用到
    def recv():
        while True:
            try:
                data = connfd.recv(1024).decode()
                if data == "!&$*#@%!*@^#$^!@&@5!&":
                    print("服务器出现异常")
                    text_recv.insert(END, "服务器出现异常")
                    t1.close()
                    os._exit(0)
                msgcon = time.strftime("%Y-%m-%d %H:%M:%S",
                                       time.localtime()) + '\n'
                text_recv.insert(END, msgcon, 'green')
                text_recv.insert(END, data)
                if data[-4:] == '已上线\n':
                    user.append(data[:-4])
                    updatelst()
                if data[-4:] == '已下线\n':
                    user.remove(data[:-4])
                    updatelst()
            except KeyboardInterrupt:
                connfd.send('＠×＆＃还７＠８＃７'.encode())
                print("已下线")
                os._exit(0)
            except Exception:
                os._exit(0)

    @classmethod
    # 客户端发送请求函数
    def send(self, obj):
        limit = Value('i', 0)

        # 单独处理下载的进程函数
        def down(value, name, v, size):
            HOST = '127.0.0.1'
            PORT = 8421
            ADDR = (HOST, PORT)
            connfd = socket()
            connfd.connect(ADDR)
            connfd.send(('开始下载' + ',' + value + ',' +
                         name + ',' + str(v)).encode())
            limitv = limit.value
            obj.jindu(value, limitv)  # 调用显示进度函数
            with open(('./download/' + value), 'wb') as f:
                while True:
                    file = connfd.recv(1024)
                    if file == b'*@!@#!!!$*':
                        break
                    f.write(file)
                    obj.jinduview(size, limitv)  # 调用显示进度函数
            print('下载成功')
            limit.value -= 1
            connfd.close()

        # 单独处理上传的进程函数
        def up(file, name, v):
            s = socket()
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', 8422))
            s.listen(5)
            obj.connfd.send(('开始上传' + ',' + file.split('/')
                             [-1] + ',' + name + ',' + str(v)).encode())
            c, addr = s.accept()
            size = os.path.getsize(file)  # 获取文件的大小
            limitv = limit.value
            obj.jindu(file.split('/')[-1], limitv)  # 调用显示进度函数
            with open(file, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    c.send(data)
                    obj.jinduview(size, limitv)  # 调用显示进度函数
                time.sleep(0.1)
            c.send('@!!#@!#$%'.encode())
            print('完成上传')
            limit.value -= 1
            view(obj.var, obj.t, obj.t1)  # 刷新列表
            s.close()

        # 下载请求函数
        def download(var):
            try:
                value = obj.filelist2.get(obj.filelist2.curselection())
                obj.connfd.send(
                    ('下载' + ',' + value + ',' + str(var.get())).encode())
                file = obj.connfd.recv(1024).decode()
                size = int(file.split(',')[1])
                if file.split(',')[0] == '可以下载':
                    if limit.value > 3:
                        print("同时只能进行３个下载任务")
                        return
                    p = Thread(target=down, args=(
                        value, obj.t.get(), var.get(), size))
                    p.start()
                    limit.value += 1
                    return
            except Exception:
                print('请选择要下载的文件')
                obj.messageboxinfo('提示', '请选择要下载的文件')

        # 上传请求函数
        def upload(var):
            file = tkinter.filedialog.askopenfilename()
            if not file:
                return
            if var.get() == 0:
                msg = obj.messageboxask(
                    '提示', '上传到共享文件夹的文件，个人用户无法对其进行删除和撤回操作，是否继续上传？')
                if not msg:
                    return
            filename = file.split('/')[-1]
            obj.connfd.send(
                ('上传' + ',' + filename + ',' + str(var.get())).encode())
            data = obj.connfd.recv(1024).decode()
            if data == '所要上传的文件名重复，请更改后重试':
                obj.messageboxinfo('提示', '所要上传的文件名重复，请重命名后再试')
            if data == '可用空间不足，请充值扩容':
                obj.messageboxinfo('提示', '可用空间不足，请充值扩容或删除部分文件后重试')
            if data == '可以上传':
                if limit.value > 3:
                    print('同时只能进行３个上传任务')
                    return
                # 创建新线程用来处理下载数据接收
                p = Thread(target=up, args=(file, obj.t.get(), var.get()))
                p.start()
                limit.value += 1
                return

        # 删除个人文件夹文件
        def delete(var):
            try:
                value = obj.filelist2.get(obj.filelist2.curselection())
                if var.get() == 0:
                    obj.messageboxinfo('提示', '无法删除共享文件夹文件')
                    return
                msg = obj.messageboxask('提示', ('是否确定删除%s?' % value))
                if not msg:
                    return
                obj.connfd.send(
                    ('删除' + ',' + value + ',' + str(var.get())).encode())
                file = obj.connfd.recv(1024).decode()
                print(file)
                if file == '删除成功':
                    obj.messageboxinfo('提示', ('成功删除文件%s' % value))
                    view(obj.var, obj.t, obj.t1)
                else:
                    obj.messageboxinfo('提示', ('删除文件%s失败' % value))
            except Exception:
                print('请选择要删除的文件')
                obj.messageboxinfo('提示', '请选择要删除的文件')

        # 通过选择单选按钮，切换显示共享或个人文件夹和用户信息函数
        def view(var, t, t1):
            r = var.get()
            obj.connfd.send(('文件夹' + ',' + str(r)).encode())
            data = obj.connfd.recv(1024).decode()
            obj.filelist2.delete(0, (len(data.split(',')) + 1))
            for i in data.split(',')[:-2]:
                obj.filelist2.insert(END, i)
            t.set(data.split(',')[-1])
            t1.set(data.split(',')[-2] + 'M')

        # 调用Gui中的sendgui函数，实现用户请求的Gui界面
        obj.sendgui(view, download, upload, delete)
        # 初始启动时显示共享文件夹
        view(obj.var, obj.t, obj.t1)
