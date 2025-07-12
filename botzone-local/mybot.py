import os
import os.path
import subprocess
import time
import threading
from queue import Queue, Empty

from botzone import Agent


class MyBot(Agent):
    def __init__(self, dirname, filename):
        self.process = None
        self.dirname = dirname
        self.filename = filename
        self.cmd = ["python", filename]
        self.output_queue = Queue()
        self.reading_thread = None
        self.monitor_thread = None
        self.waiting_for_close = False

    def reset(self):
        env = dict(os.environ)
        env["OMP_NUM_THREADS"] = "1" 
        self.process = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.dirname,
            env=env
        )

        #print("init subprocess stdin")
        self.process.stdin.write(b"\n")

        self.reading_thread = threading.Thread(target=self.start_reading)
        self.reading_thread.daemon = True
        self.reading_thread.start()

        self.monitor_thread = threading.Thread(target=self.start_monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def step(self, request):
        # 生成输入内容（示例：第1次输入，第2次输入...）
        p = self.process
        input_data = request

        # 发送输入到进程
        p.stdin.write(input_data.encode())
        p.stdin.write(b"\n")
        p.stdin.flush()
        #print(f"Send: {input_data}")

        # 等待并读取输出（带超时）
        read_timeout = 60
        output_list = []
        start_time = time.time()
        while True:
            timeout = read_timeout - (time.time() - start_time)
            if timeout <= 0:
                break
            try:
                line = self.output_queue.get(timeout=0.1)
            except Empty:
                pass
            else:
                if line:
                    if line.startswith("--"):
                        print(line)
                        continue
                    output_list.append(line)
                    #print(f"Received: {line}")
                    if line == '>>>BOTZONE_REQUEST_KEEP_RUNNING<<<':
                        return '\n'.join(output_list[:-1])
                else:
                    pass
        if output_list:
            return '\n'.join(output_list[:-1])
        return ""

    def start_reading(self):
        while True:
            if self.process.returncode is not None:
                #print(f"进程已经结束，退出码为{self.process.returncode}")
                break
            line = self.process.stdout.readline().decode().strip()
            self.output_queue.put(line)

    def start_monitor(self):
        while True:
            if self.process.returncode is not None:
                #print(f"进程已经结束，退出码为{self.process.returncode}")
                if self.process.returncode != 0:
                    errmsg = self.process.stderr.read()
                    if b"input()" not in errmsg:
                        print(f"异常退出，错误信息为：")
                        print(errmsg.decode("utf8"))
                break
            time.sleep(1)

    def close(self):
        self.waiting_for_close = True
        self.process.stdin.close()
        self.process.wait()


class MyBotFromPool(Agent):

    pool = []

    def __init__(self, dirname, filename=""):
        if not filename:
            filename = os.path.join(dirname, "__main__.py")

        for item in self.pool:
            if item["dirname"] != dirname:
                continue
            if item["filename"] != filename:
                continue
            if not item["idle"]:
                continue
            self.bot = item["bot"]
            self.botid = item["botid"]
            item["idle"] = False
            #print(f"Get MyBot {self.botid} From Pool")
            break
        else:
            self.bot = MyBot(dirname, filename)
            self.bot.reset()
            self.botid = len(self.pool) + 1
            #print(f"Create MyBot {self.botid} to Pool")
            self.pool.append({
                "dirname": dirname,
                "filename": filename,
                "idle": False,
                "bot": self.bot,
                "botid": self.botid
            })

    def reset(self):
        pass

    def step(self, request):
        return self.bot.step(request)

    def close(self):
        for item in self.pool:
            if item["botid"] == self.botid:
                #print(f"Release MyBot {item['botid']} to Pool")
                item["idle"] = True
                break


if __name__ == '__main__':
    # r"C:\MyProjects\ProgramProjects\66848fb9b54d400b709c4424"
    dirname = "."
    filename = "test_stdin.py"
    bot = MyBot(dirname, filename)
    bot.reset()
    bot.step("1")
    bot.step("2")
    bot.step("3")
    bot.close()
