try:
	# 创建名叫NoGo的游戏环境
	from botzone.online.game import Game, GameConfig
	env = Game(GameConfig.fromName('NoGo'))
	# 创建两个Bot实例，ID均为5fede20fd9383f7579afff06（这是样例Bot）
	from botzone.online.bot import Bot, BotConfig
	bots = [Bot(BotConfig.fromID('5fede20fd9383f7579afff06')) for i in range(env.player_num)]
	# 指定对局玩家
	env.init(bots)
	# 运行对局并渲染画面
	score = env.reset()
	env.render()
	while score is None:
		score = env.step() # 对局结束时，step会以tuple的形式返回各玩家得分
		env.render()
	print(score)
finally:
	# 对于包装的游戏和Bot，必须保证程序结束前调用close以释放沙盒资源，将该代码放在finally块中可以保证在程序出错退出前仍然能够执行。如果不释放沙盒资源，一段时间后你的电脑中会运行着许多docker容器实例，需要手动杀死。
	# 对于自定义的Env和Agent也建议在结束前调用close，因为它们可能需要释放资源
	env.close()
	for bot in bots: bot.close()