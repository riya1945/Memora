from memora.agent.agent import run_agent


def main():
    question = input("You: ")
    response = run_agent(question)
    print(f"\nMemora: {response}")


if __name__ == "__main__":
    main()