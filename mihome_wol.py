import os
import threading
import subprocess
import configparser
from paho.mqtt import client as mqtt_client

# Bemfa MQTT
bemfa_broker = ''
bemfa_port = 1883
bemfa_topic = ''
bemfa_client_id = ''

# WOL
wol_mac = ''
wol_ip = ''
wol_user = ''
wol_password = ''

# 收到订阅的主题消息后，进行处理：开机/关机
def mqtt_handle(data):
    try:
        if "on" in data:
            process = subprocess.Popen(
                ['etherwake', '-i', 'br-lan', wol_mac],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        elif "off" in data:
            process = subprocess.Popen(
                ['sshpass', '-p', wol_password, 'ssh', f'{wol_user}@{wol_ip}', 'psshutdown64.exe -d -t 0 -accepteula'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            log_message(f"Unknown command: {data}")
            return

        # 实时读取输出
        for line in process.stdout:
            log_message(f"STDOUT: {line.strip()}")
        for line in process.stderr:
            log_message(f"STDERR: {line.strip()}")

        # 等待进程结束并获取返回码
        process.wait(timeout=5)
        log_message(f"Command finished with return code: {process.returncode}")

    except subprocess.TimeoutExpired:
        process.kill()
        log_message(f"Command '{data}' timed out and was terminated.")
    except Exception as e:
        log_message(f"Error executing command: {e}")

# 连接巴法 MQTT 服务器并订阅主题
def connect_bemfa() -> mqtt_client:
    def on_message_bemfa(client, userdata, msg):
        message = msg.payload.decode()
        log_message(f'Received message "{message}" from topic "{msg.topic}"')
        mqtt_handle(message)

    def on_connect_bemfa(client, userdata, flags, rc):
        if rc == 0:
            log_message("Connected to Bemfa Broker!")
        else:
            log_message(f"Failed to connect, return code {rc}")
        client.subscribe(topic=bemfa_topic, qos=1)
        client.on_message = on_message_bemfa
    
    client = mqtt_client.Client(client_id=bemfa_client_id, clean_session=False)
    client.on_connect = on_connect_bemfa
    client.connect(bemfa_broker, bemfa_port, keepalive=120)
    return client

# 使用 OpenWRT 的 logger 记录日志
def log_message(message):
    os.system(f"logger -p info -t mihome_wol -s '{message}'")

# MQTT 任务
def task_bemfa_wol():
    client_bemfa = connect_bemfa()
    client_bemfa.loop_forever()

if __name__ == '__main__':
    config = configparser.ConfigParser(interpolation=None)

    # 读取 INI 文件
    config.read('./config.ini')
    bemfa_broker = config.get('MQTT_CONFIG', 'bemfa_broker')
    bemfa_port = int(config.get('MQTT_CONFIG', 'bemfa_port'))
    bemfa_topic = config.get('MQTT_CONFIG', 'bemfa_topic')
    bemfa_client_id = config.get('MQTT_CONFIG', 'bemfa_client_id')
    wol_mac = config.get('WOL_CONFIG', 'wol_mac')
    wol_ip = config.get('WOL_CONFIG', 'wol_ip')
    wol_user = config.get('WOL_CONFIG', 'wol_user')
    wol_password = config.get('WOL_CONFIG', 'wol_password')

    # 运行 MQTT 任务
    task_bemfa = threading.Thread(target=task_bemfa_wol, name='Bemfa_WOL')
    task_bemfa.start()
    task_bemfa.join()
