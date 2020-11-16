# distributed-key

生成的种子密钥在相对路径"Information\Priviate_info\self_info\group_key.txt"

组播环境过于严苛，于是放弃，选择对每个IP单播。



此版本为无GUI版本，每次输入打开程序之后需要输入用户名，若输入用户名与本地文件中存储用户名一致则保留本地文件，否则将本地文件清空，并将新输入的名字替换原来的信息

![image-20201116164647455](C:\Users\17968\AppData\Roaming\Typora\typora-user-images\image-20201116164647455.png)

输入本地中保存的用户名之后，会出现如下界面

![image-20201116164720962](C:\Users\17968\AppData\Roaming\Typora\typora-user-images\image-20201116164720962.png)

输入非本地中保存的用户名会出现

![image-20201116165113593](C:\Users\17968\AppData\Roaming\Typora\typora-user-images\image-20201116165113593.png)

上面两张图中显示的提示信息都是**普通节点**的，只需输入对应序号1，2，3，4，5，q即可。

Register即注册，之后会要求输入注册指向的管理节点IP

![image-20201116165627177](C:\Users\17968\AppData\Roaming\Typora\typora-user-images\image-20201116165627177.png)

Retreat即退出群组

Group_session_key_calculation即计算密钥种子，最终密钥种子文件保存在相对路径"Information\Priviate_info\self_info\group_key.txt"中

Public_info_receiving 即接收群广播函数，主要是当群组中删除群成员之后接收管理节点发送的公共信息用于计算新的密钥种子

Infoupdate是将信息保存到本地的函数

exit即退出程序

下面展示一下**管理节点**的界面

![image-20201116170637017](C:\Users\17968\AppData\Roaming\Typora\typora-user-images\image-20201116170637017.png)

此处需要指出的一点是管理节点是通过本地文件指出的即需要手动修改"Information\Priviate_info\manager_info\manager_info.txt"中的class对应值为"Manager"

![image-20201116170919402](C:\Users\17968\AppData\Roaming\Typora\typora-user-images\image-20201116170919402.png)

同时还有一点值得注意的是，每当输入用户名与本地用户名不一致时都会自动将此处的值改为"Oridnary"即不能再当作管理节点使用

此处详细列举各项功能

Monitor是用于监控普通节点发出的注册，撤销等信息

Infoupdate是用于保存信息到本地

Deluser是用于删除用户，之后会要求输入需要删除的用户的用户名

![](C:\Users\17968\AppData\Roaming\Typora\typora-user-images\image-20201116171459260.png)

ClearUserlist是用于清理本地文件缓存，每次接收注册之后都会将注册者的用户名写入文件"Information\Priviate_info\manager_info\userlist.txt"中这样可以避免重复注册，但当出现一些较极端情况可以快速清理整个列表的话就可以快速断开与所有注册者的连接

![image-20201116172015562](C:\Users\17968\AppData\Roaming\Typora\typora-user-images\image-20201116172015562.png)

这个图片中group_key.txt中存储的就是计算得到的种子密钥，self_info.txt中存储的节点的群组会话信息

![image-20201116172326559](C:\Users\17968\AppData\Roaming\Typora\typora-user-images\image-20201116172326559.png)

图中manager_info.txt中存储了节点的性质即是否是管理节点，和与之有注册关系的群组成员，userlist.txt中存储的是当前已经注册且未被删除的节点用户名