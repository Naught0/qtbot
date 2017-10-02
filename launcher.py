from bot import QTBot
import sys

def main():
    try:
        config_file = sys.argv[1]
    except:
        config_file = 'data/apikeys.json'

    bot = QTBot(config_file)
    bot.run()

if __name__ == '__main__':
    main()
