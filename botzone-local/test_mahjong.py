import os
import time

from botzone.envs.botzone.chinesestandardmahjong import ChineseStandardMahjongEnv
from botzone.online.game import GameConfig
from mybot import MyBot
# from mygame import MyGame
#
# env = MyGame(GameConfig.fromName('ChineseStandardMahjong'))

initdata = {
    "quan": 2,
    "srand": 1697864911,
    "walltiles": "W6 T4 B7 B5 B8 W2 W6 T6 T2 B3 B5 W1 W6 W2 W4 T9 T1 W5 B2 B5 J2 W9 F1 W3 T2 T7 B8 T8 W1 F3 J1 B7 J2 J1 F3 W8 W5 T7 F1 F3 B6 T5 B7 B4 T8 B2 W8 T3 W7 T3 F3 T5 F2 F1 B1 W5 T1 W5 B3 J1 W8 B8 T7 B4 B3 W3 T7 T8 B9 F2 F4 F2 W9 B1 T4 B4 T5 T6 B9 T9 J3 F4 W7 T3 T1 F2 J1 W6 T2 W8 F4 J3 B2 W3 T9 W4 B4 B6 W4 J2 B6 W9 T4 W4 F1 J3 B1 T3 B7 B3 W1 T2 T1 T6 T8 W2 W1 B1 B6 W9 T4 J3 W7 B2 T5 J2 B9 B5 W3 T6 B9 T9 W7 W2 B8 F4"
}

env = ChineseStandardMahjongEnv(duplicate=True)
#bots = [MyBot(dirname=r"C:\MyProjects\ProgramProjects\66848fb9b54d400b709c4424", filename=r"C:\MyProjects\ProgramProjects\66848fb9b54d400b709c4424\__main__.py") for i in range(env.player_num)]
bots = [MyBot(dirname=r"C:\MyProjects\ProgramProjects\mahjong", filename=r"C:\MyProjects\ProgramProjects\mahjong\__main__.py") for i in range(env.player_num)]

bots[0] = MyBot(dirname=r"D:\Projects\mahjong-versions\v1_vecfix", filename=r"D:\Projects\mahjong-versions\v1_vecfix\__main__.py")

try:
    # 指定对局玩家
    env.init(bots)
    # 运行对局并渲染画面
    score = env.reset(initdata=initdata)
    env.render()
    while score is None:
        score = env.step()  # 对局结束时，step会以tuple的形式返回各玩家得分
        #os.system("cls")
        env.render()
    print(score)
except Exception as ex:
    import traceback
    traceback.print_exc()
    raise
finally:
    # 对于包装的游戏和Bot，必须保证程序结束前调用close以释放沙盒资源，将该代码放在finally块中可以保证在程序出错退出前仍然能够执行。如果不释放沙盒资源，一段时间后你的电脑中会运行着许多docker容器实例，需要手动杀死。
    # 对于自定义的Env和Agent也建议在结束前调用close，因为它们可能需要释放资源
    env.close()
    for bot in bots:
        bot.close()
