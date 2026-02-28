from __future__ import annotations

from enum import Enum, auto
from typing import Any, Optional
import hashlib
import openai

from .data import ChatWeaverModelNames


# Cache globali: NON salvare la key in chiaro, meglio una fingerprint
_cache_api_key_fp: set[str] = set()
_cache_model_name: set[str] = set()


class KeyStatus(str, Enum):
    MISSING = auto()
    UNKNOWN = auto()
    VALID = auto()
    INVALID = auto()

    def __str__(self) -> str:
        return f"<{self.name.upper()}>"

    def __repr__(self) -> str:
        return self.__str__()


class Model(object):
    """
    Wrapper robusto che separa:
      - state (snapshot/freeze): model, api_key (opzionale), extra serializzabili
      - capability runtime: client, key_status, last_auth_error

    L'istanza può esistere anche con api_key mancante o errata.
    I servizi esterni (client) sono disponibili solo se la key risulta valida.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = ChatWeaverModelNames.gpt_4o, **kwargs) -> None:
        # capabilities
        self.__client: Optional[openai.OpenAI] = None
        self.__key_status: KeyStatus = KeyStatus.MISSING
        self.__last_auth_error: Optional[str] = None

        # init "from snapshot"
        if "define" in kwargs:
            attributes: dict[str, dict[str, Any]] = kwargs["define"]
            props: dict[str, Any] = attributes.get("properties", {})
            extra: dict[str, Any] = attributes.get("extra", {})

            for k, v in props.items():
                setattr(self, k, v)

            for k, v in extra.items():
                setattr(self, k, v)

            if self.api_key is None:
                self.__key_status = KeyStatus.MISSING
            else:
                if self.__key_status is not KeyStatus.INVALID:
                    self.__key_status = KeyStatus.UNKNOWN

            return

        # normal init
        self.model = model
        self.api_key = api_key

    # -------- FREEZE | THAW --------
    def freeze(self, include_secrets: bool = False) -> dict[str, Any]:
        """
        Snapshot serializzabile.
        Di default NON include la api_key (per sicurezza).
        Se include_secrets=True, include api_key nello snapshot.
        """
        props: dict[str, Any] = {
            "model": self.model,
        }

        if include_secrets:
            props["api_key"] = self.api_key

        return {
            "properties": props,
            "extra": {
            },
        }

    @classmethod
    def thaw(cls, snapshot: dict[str, Any], api_key: Optional[str] = None) -> "Model":
        """
        Ricrea l'istanza da snapshot.
        Se api_key è passata, sovrascrive quella eventualmente presente nello snapshot.
        """
        inst = cls(api_key=None, define=snapshot)
        if api_key is not None:
            inst.api_key = api_key
        return inst

    # -------- UTILS --------
    def _api_key_fingerprint(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    def api_key_hint(self) -> str:
        k = self.api_key
        if not k:
            return "<none>"
        if len(k) <= 12:
            return "<set>"
        return f"{k[:6]}...{k[-4:]}"


    # -------- MAGIC METHODS --------
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} | model: {self.model!r}, api_key: {self.api_key_hint()!r}, key_status: {self.__key_status}>"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model!r}, api_key={self.api_key_hint()!r}, key_status={self.__key_status!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.model == other.model and self.api_key == other.api_key

    # -------- PROPERTIES --------
    @property
    def model(self) -> str:
        return self.__model
    @model.setter
    def model(self, new_model: str) -> None:
        global _cache_model_name
        new_model = str(new_model)

        if new_model not in _cache_model_name:
            if new_model not in ChatWeaverModelNames.get_all_models():
                raise ValueError(f"'{new_model}' is not acceptable.")
            _cache_model_name.add(new_model)

        self.__model = new_model

    @property
    def api_key(self) -> Optional[str]:
        return getattr(self, "_Model__api_key", None)
    @api_key.setter
    def api_key(self, new_api_key: Optional[str]) -> None:
        """
            Setter does NOT perform network calls. It never blocks the instance.
            It is limited to:
              - updating __api_key
              - resetting the runtime client
              - setting a consistent key_status (MISSING / UNKNOWN / INVALID)
        """

        # reset capability runtime
        self.__client = None
        self.__last_auth_error = None

        if not new_api_key:
            self.__api_key = None
            self.__key_status = KeyStatus.MISSING
            return

        new_api_key = str(new_api_key).strip()
        self.__api_key = new_api_key

        # "soft" check: if it fails, it does NOT prevent existence, but marks it as INVALID
        if not new_api_key.startswith("sk-") or len(new_api_key) < 20:
            self.__key_status = KeyStatus.INVALID
            self.__last_auth_error = "Invalid API key format."
            return

        # Do not validate here: it will be lazily validated when needed
        self.__key_status = KeyStatus.UNKNOWN

    @property
    def key_status(self) -> KeyStatus:
        return self.__key_status
    @property
    def last_auth_error(self) -> Optional[str]:
        return self.__last_auth_error

    # -------- VALIDATION --------
    def validate_api_key(self) -> bool:
        """
            Actually validates the api_key by performing a lightweight call (models.list()).
            If it fails:
              - it does not break the instance
              - sets key_status to INVALID and last_auth_error
              - the client remains None
        """

        api_key = self.api_key

        if not api_key:
            self.__key_status = KeyStatus.MISSING
            self.__client = None
            return False

        # skip network calls if already invalid by format
        if self.__key_status is KeyStatus.INVALID and self.__last_auth_error == "Invalid API key format.":
            self.__client = None
            return False

        fp = self._api_key_fingerprint(api_key)
        if fp in _cache_api_key_fp:
            # treat it as valid and recreate the client if necessary
            self.__key_status = KeyStatus.VALID
            if self.__client is None:
                self.__client = openai.OpenAI(api_key=api_key)
            return True

        try:
            client = openai.OpenAI(api_key=api_key)
            client.models.list()  # check credentials
            self.__client = client
            self.__key_status = KeyStatus.VALID
            _cache_api_key_fp.add(fp)
            return True
        except Exception as e:
            self.__client = None
            self.__key_status = KeyStatus.INVALID
            self.__last_auth_error = str(e)
            return False

    @property
    def client(self) -> openai.OpenAI:
        """
            Lazy client: if not available, it attempts validation.
            If the key is not valid, it raises a clear error BUT the instance remains intact.
        """

        if self.__client is not None and self.__key_status is KeyStatus.VALID:
            return self.__client

        ok = self.validate_api_key()
        if not ok:
            fp = self._api_key_fingerprint(self.api_key)
            if fp in _cache_api_key_fp:
                _cache_api_key_fp.remove(fp)
            raise RuntimeError(
                f"Client not available: key_status={self.__key_status}. "
                f"Reason: {self.__last_auth_error or 'missing/invalid api_key'}"
            )

        assert self.__client is not None
        return self.__client

    def can_use_remote_services(self) -> bool:
        """
            True if the client can be used (valid key).
            Does not force calls if already MISSING or formally INVALID.
        """

        if self.__key_status is KeyStatus.VALID:
            return True
        if self.__key_status is KeyStatus.MISSING:
            return False
        if self.__key_status is KeyStatus.INVALID and self.__last_auth_error == "Invalid API key format.":
            return False
        # UNKNOWN or INVALID from network: try to validate
        return self.validate_api_key()
