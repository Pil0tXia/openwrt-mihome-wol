# OpenWRT-MiHome-WOL

该项目通过将 OpenWRT 路由器接入米家，实现远程控制 PC、开关机等功能。

## 功能介绍

- 通过[巴法云](https://bemfa.com/) MQTT 协议接收米家 APP 的指令
- 使用 Wake-on-LAN (WOL) 包远程开机
- 使用 SSH 远程登录并执行关机、休眠、睡眠或其他命令
- 代码精简，高度配置化，可定制开发

## 快速开始

### 配置

1. 安装依赖库和工具

```shell
opkg update
opkg install python3-base
opkg install python3-pip
opkg install python3
opkg install etherwake
opkg install sshpass

pip3 install -i https://pypi.doubanio.com/simple paho-mqtt==2.1.0
```

2. 克隆项目代码

```shell
git clone https://github.com/Pil0tXia/openwrt-mihome-wol.git
cd openwrt-mihome-wol
```

3. 填写配置文件

```shell
cp config.example.ini config.ini
vi config.ini
```

配置示例：

```shell
[MQTT_CONFIG]
bemfa_broker=bemfa.com
bemfa_port=9501
# 巴法平台的主题名/设备名
bemfa_topic=pc006
# 巴法平台控制台获取的私钥
bemfa_client_id=b******************************5

[WOL_CONFIG]
# 目标主机的MAC地址，windows下打开CMD输入命令ipconfig /all查看
wol_mac=4E:C0:5A:3B:F1:2D
# 目标主机的IP地址，windows下打开CMD输入命令ipconfig /all查看
wol_ip=192.168.1.100
# 目标主机的用户名
wol_user=administrator
# 目标主机的密码
wol_password=password
```

巴法平台的主题名/设备名和私钥于[巴法 MQTT 设备云](https://cloud.bemfa.com/tcp/devicemqtt.html)获取。

4. （可选）Windows S3 经典睡眠工具

在 PC 上，于 https://learn.microsoft.com/en-us/sysinternals/downloads/psshutdown 下载 PsTools，并将其文件夹路径添加到系统 PATH。

### 运行

```shell
python3 mihome_wol.py
```

### 自启动

在`/etc/rc.local`文件中添加以下内容：

```shell
cd /root/your/path/to/openwrt-mihome-wol && nohup python3 mihome_wol.py > /dev/null 2>&1 &
```

启动脚本的命令插入到`exit 0`之前即可随系统启动运行。

### 米家指令

```
小爱同学，开电脑
小爱同学，关电脑
```

其中，“电脑”的名称取自巴法云中的设备昵称。

## 注意事项

- 请确保路由器和 PC 在同一局域网内。
- 请确保 PC 已启用 Wake-on-LAN 和 SSH 功能。

## 鸣谢

感谢[cgy233/EthanHome-WOL](https://github.com/cgy233/EthanHome-WOL)为本项目提供的灵感。
