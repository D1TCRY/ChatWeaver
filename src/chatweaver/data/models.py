import inspect


class _ChatWeaverModelNames:
    def __init__(self):
        self.__locked = False

        # Current OpenAI text/chat models compatible with the Chat Completions
        # pattern used by Bot.completion(). Aliases track moving targets; dated
        # snapshots lock behavior for reproducible results.

        # GPT-5.5 / GPT-5.4 families
        self.gpt_5_5 = "gpt-5.5"
        self.gpt_5_5_2026_04_23 = "gpt-5.5-2026-04-23"
        self.gpt_5_5_pro = "gpt-5.5-pro"
        self.gpt_5_5_pro_2026_04_23 = "gpt-5.5-pro-2026-04-23"
        self.gpt_5_4 = "gpt-5.4"
        self.gpt_5_4_2026_03_05 = "gpt-5.4-2026-03-05"
        self.gpt_5_4_mini = "gpt-5.4-mini"
        self.gpt_5_4_mini_2026_03_17 = "gpt-5.4-mini-2026-03-17"
        self.gpt_5_4_nano = "gpt-5.4-nano"
        self.gpt_5_4_nano_2026_03_17 = "gpt-5.4-nano-2026-03-17"

        # GPT-5 previous/current aliases and ChatGPT-style aliases
        self.gpt_5_3_chat_latest = "gpt-5.3-chat-latest"
        self.gpt_5_2 = "gpt-5.2"
        self.gpt_5_2_chat_latest = "gpt-5.2-chat-latest"
        self.gpt_5_1 = "gpt-5.1"
        self.gpt_5_1_2025_11_13 = "gpt-5.1-2025-11-13"
        self.gpt_5_1_chat_latest = "gpt-5.1-chat-latest"
        self.gpt_5 = "gpt-5"
        self.gpt_5_mini = "gpt-5-mini"
        self.gpt_5_mini_2025_08_07 = "gpt-5-mini-2025-08-07"
        self.gpt_5_nano = "gpt-5-nano"
        self.gpt_5_nano_2025_08_07 = "gpt-5-nano-2025-08-07"

        # GPT-4 generation kept for compatibility and lower-risk migrations
        self.gpt_4_1 = "gpt-4.1"
        self.gpt_4_1_2025_04_14 = "gpt-4.1-2025-04-14"
        self.gpt_4_1_mini = "gpt-4.1-mini"
        self.gpt_4_1_nano = "gpt-4.1-nano"
        self.gpt_4o = "gpt-4o"
        self.gpt_4o_mini = "gpt-4o-mini"
        self.gpt_4_turbo = "gpt-4-turbo"
        self.gpt_4 = "gpt-4"

        # Reasoning / legacy models useful for existing archives and tests
        self.o3 = "o3"
        self.o3_pro = "o3-pro"
        self.o4_mini = "o4-mini"
        self.o3_mini = "o3-mini"
        self.o1 = "o1"
        self.o1_pro = "o1-pro"
        self.o1_mini = "o1-mini"

        self.__locked = True
        
    
    def default(self) -> str:
        return self.gpt_5_5

    # -------- HELPERS --------
    def __get_attributes(self):
        attributes: dict = {}
        exceptions: list = []

        for attr_name in dir(self):
            if attr_name.startswith("_"):
                continue

            try:
                attr_value = getattr(self, attr_name)
                if not inspect.isroutine(attr_value):
                    attributes[attr_name] = attr_value
            except Exception as exc:
                exceptions.append(exc)
                continue

        return attributes

    def __set_lock(self, state: bool | None = None) -> None:
        if not isinstance(state, (bool, type(None))):
            raise TypeError("<Invalid 'state' type, must be a 'bool' object>")

        if state is None:
            object.__setattr__(self, self.__class__.__name__+"__locked", not self.__locked)
        else:
            object.__setattr__(self, self.__class__.__name__+"__locked", state)


    # -------- DUNDERS --------
    def __str__(self) -> str:
        dictionary = {name: getattr(self, name) for name in self.__get_attributes()}
        return repr(dictionary)

    def __repr__(self) -> str:
        return self.__str__()

    def __iter__(self):
        for name in self.__get_attributes():
            yield name, getattr(self, name)

    def __delattr__(self, name: str) -> None:
        if hasattr(self, self.__class__.__name__+"__locked") and self.__locked:
            raise SyntaxError("< ChatWeaverModelNames | Cannot delete attributes from this object >")

        object.__delattr__(self, name)

    def __setattr__(self, name: str, value) -> None:
        if hasattr(self, self.__class__.__name__+"__locked") and self.__locked:
            raise SyntaxError("< ChatWeaverModelNames | Cannot set attributes from this object >")

        object.__setattr__(self, name, value)


    # -------- PUBLIC METHODS --------
    def add(self, model: str) -> None:
        existing_values = list(self.__get_attributes().values())

        if model in existing_values:
            return

        model = model.strip()
        attr_name = model.replace("-", "_").replace(".", "_")

        if not attr_name.isidentifier() or attr_name.startswith("_"):
            raise AttributeError(f"<Invalid model name: {repr(attr_name)}>")

        self.__set_lock(False)
        try:
            setattr(self, attr_name, model)
        finally:
            self.__set_lock(True)

    def delete(self, model: str) -> None:
        existing_models = self.get_all_models()
        # find the correct name_attr
        name_attr = model.replace("-", "_").replace(".", "_")

        if name_attr not in list(self.__get_attributes().keys()):
            return

        self.__set_lock(False)
        try:
            delattr(self, name_attr)
        finally:
            self.__set_lock(True)

    def get_all_models(self) -> list[str]:
        return list(self.__get_attributes().values())

ChatWeaverModelNames = _ChatWeaverModelNames()


if __name__ == "__main__":
    models = ChatWeaverModelNames

    print("Modelli iniziali:")
    print(models)
    print()

    # Test iterazione
    print("Iterazione:")
    for name, value in models:
        print(f"  {name}: {value}")
    print()

    # Test aggiunta modello
    print("Aggiungo 'claude-3-opus':")
    models.add("claude-3-opus")
    print(models)
    print()

    # Test aggiunta duplicato (non fa nulla)
    print("Aggiungo di nuovo 'gpt-4' (nessun effetto):")
    models.add("gpt-4")
    print(models)
    print()

    print("Test tentativo di modifica (errore)")
    try:
        models.gpt_4 = "nuovo-valore"
    except SyntaxError as e:
        print(f"Errore atteso: {e}")
    print("\n")

    # Test tentativo di cancellazione (errore)
    try:
        del models.gpt_4
    except SyntaxError as e:
        print(f"Errore atteso: {e}")

    print("\n", models)

    print("\ndeleting model\n")
    models.delete("claude_3-opus")

    print(models)
