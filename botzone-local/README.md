# Botzone本地环境

基于 https://github.com/ailab-pku/botzone-local.git 做的特化本地化修改，仅使用复式麻将环境，不使用容器，并且支持智能体不退出直接自动重置状态
裁判代码基于 https://github.com/ailab-pku/Chinese-Standard-Mahjong.git/judge 进行修改，将进程改为了lib，显著提高运行效率

使用方法：

```bash
# 编译裁判lib，用于判定游戏是否结束
python setup.py build_ext --inplace

# 更改智能体路径配置，改为你想要参与评测的智能体路径。更改方式见后文

# 只进行一局游戏并展示游戏运行过程。此运行文件的所有配置都在该文件内，自己看着改
python test_mahjong.py

# 单进程运行
python mahjong_race.py

# 多进程运行
python mahjong_race_mp.py

# mahjong_race_parallel基于传统subprocess多进程，已停止维护，不建议使用
```

参与运行的智能体路径需要在以下地方进行配置

    mahjong_race,py BASELINE_FILENAME 
	baseline模型，若参与游戏的智能体数量不到4，则自动用该值补位。多进程版本的Baseline复用此变量

	mahjong_race.py def main() filenames
	mahjong_race_mp.py def main() filenames
	单进程/多进程版本，参与游戏的智能体路径。暂未支持对每个智能体传入不同的环境变量或不同的命令行参数。

	def main() start_seed、round_count、process_count
	起始种子、游戏局数、进程数（仅多进程版本）

程序运行逻辑：

    从起始种子开始，每局种子+1，确保运行结果可复现

	单进程版本，主进程为裁判进程，会启动4个智能体进程，依次进行游戏
	多进程版本，每4秒启动一个裁判进程，裁判进程会启动4个智能体进程，从队列中获取游戏信息并进行游戏
	（每4秒间隔启动，防止所有裁判进程下属的智能体进程同时初始化，导致初始化超时判定为失败）

	每局游戏，由4个智能体进程交替进行24次全排列游戏，将结算的所有分数加起来衡量名次，根据名次赋分
	如果智能体路径有重复，则因为重复的智能体交换运行的结果完全一致，交替进行游戏的次数会下降
	（本人常用策略：使用1个智能体与3个Baseline进行游戏，只需要进行4局游戏即可完成全排列，效率显著提升）
	如果存在同名次的情况，则它们同分。比如1个智能体与3个Baseline进行游戏，有3种分数分布结果：4444、4333、3444。

	游戏结果将按照种子的顺序依次输出到命令行，并保存到race_result_{timestamp}.json

