"""Mock LLM used for offline lab runs."""
import random
import time


MOCK_RESPONSES = {
    "default": [
        "This is a mock AI response. The deployment pipeline is working.",
        "Agent is running correctly with the local mock LLM.",
        "Your request reached the production-style agent successfully.",
    ],
    "docker": [
        "Docker packages the app and its dependencies so it can run consistently anywhere."
    ],
    "deploy": [
        "Deployment moves the service from your machine to a cloud runtime with a public URL."
    ],
    "health": [
        "The agent is healthy and ready to receive traffic."
    ],
}


def ask(question: str, delay: float = 0.05) -> str:
    time.sleep(delay + random.uniform(0, 0.02))
    lowered = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in lowered:
            return random.choice(responses)
    return random.choice(MOCK_RESPONSES["default"])
