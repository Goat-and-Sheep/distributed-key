from Manage_Point import *
import os

if __name__ == "__main__":
    T0 = ManagePoint()
    username = input("请输出用户名: ")
    if T0.ID == username:
        print("您已经是一个成熟的用户了需要自己掌握注册等技巧")
    else:
        print("您是一个新用户！")
        T0.ID = username
        T0.pkey = ""
        T0.vector = []
        T0.intz = 0
        T0.gc = {"IP": "", "USER_ID": ""}
        T0.groupkey = 0
        T0.Class = "Oridinary"
        T0.infoupdate()
        path = "Information/Priviate_info/self_info/privkeyfordecrypt.pem"
        if (os.path.exists(path)):
            os.remove(path)
        path = "Information/Priviate_info/self_info/privkeyforsign.pem"
        if (os.path.exists(path)):
            os.remove(path)
        path = "Information/Priviate_info/self_info/pubkeyforencrypt.pem"
        if (os.path.exists(path)):
            os.remove(path)
        path = "Information/Priviate_info/self_info/pubkeyforverify.pem"
        if (os.path.exists(path)):
            os.remove(path)
        print("初始化成功！")
    if T0.Class == "Manager":
        print("(1)Monitor (2)Infoupdate (3)Deluser (4)ClearUserlist (q)exit")
        while True:
            command = input("输入相应序号:  ")
            if command == "1":
                T0.Monitor()
            elif command == "2":
                T0.infoupdate()
            elif command == "3":
                info = input("请输入需要删除的节点的ID: ")
                T0.deluser(info)
            elif command == "4":
                List = []
                filewrite.write(
                    "Information/Priviate_info/manager_info/userlist.txt", List)
            elif command == "q":
                break
            else:
                print("请输入正确的指令")
    else:
        print("(1)Register (2)Retreat (3)Group_session_key_calculation (4)Public_info_receiving (5)Infoupdate (q)exit")
        while True:
            command = input("输入相应序号:  ")
            if command == "1":
                info = input("请输入管理节点的IP:   ")
                T0.node_registration(info)
                judge = input("是否保存注册信息？[Y/N]")
                if judge == "Y":
                    T0.infoupdate()
            elif command == "2":
                T0.node_retreat()
            elif command == "3":
                T0.group_session_key_calculation()
                print("种子密钥已经被保存到\"Information\Priviate_info\self_info\group_key.txt\"")
            elif command == "4":
                T0.public_info_receiving()
            elif command == "5":
                T0.infoupdate()
            elif command == "q":
                break
            else:
                print("请输入正确的指令")
