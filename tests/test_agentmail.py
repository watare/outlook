import types

import agentmail

class FakeChatCompletion:
    def __init__(self):
        self.calls = []

    def create(self, model, messages):
        self.calls.append((model, messages))
        class Resp:
            choices = [types.SimpleNamespace(message={"content": "Summary"})]
        return Resp()

def test_analyze_message(monkeypatch):
    fake = FakeChatCompletion()
    monkeypatch.setattr(agentmail.openai, "ChatCompletion", fake)
    result = agentmail.analyze_message("Hello")
    assert result == "Summary"
    assert fake.calls
