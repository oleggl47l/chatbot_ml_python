from bot import run_bot
from nlp.intent_model import IntentClassifier


def main():
    classifier = IntentClassifier()
    classifier.train()

    run_bot()

if __name__ == "__main__":
    main()
