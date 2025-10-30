
from euchre_core import EuchreEngine
from bots.random_bot import RandomBot
from bots.rule_bot import RuleBot

def play_hand(bot0, bot1, bot2, bot3, seed=0):
    env = EuchreEngine(seed=seed)
    obs, mask, kind = env.observation(), env.mask(), env.action_kind()
    done=False
    while not done:
        seat = obs["seat"]
        action = [bot0,bot1,bot2,bot3][seat].act(obs, mask, kind)
        obs, mask, kind, reward, done, info = env.step(action)
    return env.points, info

if __name__ == "__main__":
    points, info = play_hand(RandomBot(1), RuleBot(), RandomBot(2), RuleBot(), seed=42)
    print("Final points:", points, "info:", info)
