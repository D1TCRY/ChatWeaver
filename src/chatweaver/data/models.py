import inspect


class _ChatWeaverModelNames:
    def __init__(self):
        self.__locked = False

        self.gpt_4 = "gpt-4"
        self.gpt_4o = "gpt-4o"
        self.gpt_4_turbo = "gpt-4-turbo"
        self.o1 = "o1"
        self.o1_mini = "o1-mini"
        self.o3 = "o3"

        self.__locked = True

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
