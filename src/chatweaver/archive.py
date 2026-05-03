from __future__ import annotations

import os
import json
import asyncio
from typing import Any, Callable, Optional, Dict, Sequence, Awaitable

from .model import Model
from .bot import Bot
from .chat import Chat
from .text_node import TextNode




class Archive(object):
    """
    Manages an archive of Chat, Bot, or Model objects stored at a file path.
    """

    def __init__(self, path: str, api_key: str | None = None, asynchronous: bool = True, delay: float = 0.07) -> None:
        """
        Initializes an archive with a file path and loading options.
        """
        self.path = path
        self.api_key = api_key
        self.asynchronous = asynchronous
        self.delay = delay

        # Internal cache
        self.__data: dict[int, Chat | Bot | Model] = {}
        self.__data_is_modified: bool = True  # force first load

        # Warm load
        _ = self.data

    # -------- MAGIC METHODS --------
    def __str__(self) -> str:
        _ = 6
        return f"<Archive | path: {self.__path!r}, length: {len(self.data)}, api_key: {(self.api_key[:_]+'...'+self.api_key[-_:] if len(self.api_key) > 2*_+3 else self.api_key)!r}>"

    def __repr__(self) -> str:
        return f"Archive(path={self.__path!r})"

    def __len__(self) -> int:
        return len(self.data)

    def __add__(self, other: Chat | Bot | Model):
        if not isinstance(other, (Chat, Bot, Model)):
            raise TypeError(f"<Unexpected type. Expected Chat or Bot or Model, got {type(other)}>")
        self.add(other)
        return self

    def __sub__(self, other: int | Chat | Bot | Model):
        if isinstance(other, int):
            self.remove(element=other)
            return self
        if isinstance(other, (Chat, Bot, Model)):
            self.remove(element=other)
            return self
        raise TypeError(f"<Unexpected type. Expected int or Chat or Bot or Model, got {type(other)}>")

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.save()

    # -------- PROPERTIES --------
    @property
    def path(self) -> str:
        """Returns the archive file path."""
        return self.__path

    @path.setter
    def path(self, new_path: str) -> None:
        """Sets the archive file path and ensures the file exists."""
        new_path = str(new_path).strip()
        if len(new_path) == 0:
            raise ValueError("<Invalid 'path': cannot be empty>")

        # Create parent folders if needed
        parent = os.path.dirname(os.path.abspath(new_path))
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)

        # Create the archive file if missing
        if not os.path.exists(new_path):
            with open(new_path, "w") as f:
                f.write("")  # keep empty to preserve current retrieve() semantics

        self.__path = new_path
        self.__data_is_modified = True

    @property
    def api_key(self) -> str | None:
        return self.__api_key
    @api_key.setter
    def api_key(self, new_api_key: str | None) -> None:
        self.__api_key = str(new_api_key) if new_api_key is not None else None

    @property
    def asynchronous(self) -> bool:
        """Returns whether the archive loads asynchronously."""
        return self.__asynchronous

    @asynchronous.setter
    def asynchronous(self, new_asynchronous: bool) -> None:
        """Enables or disables asynchronous loading."""
        if not isinstance(new_asynchronous, bool):
            raise TypeError(f"<Unexpected type for 'asynchronous'. Expected bool, got {type(new_asynchronous)}>")
        self.__asynchronous = new_asynchronous

    @property
    def delay(self) -> float:
        """Returns the delay used between async loading attempts."""
        return self.__delay

    @delay.setter
    def delay(self, new_delay: float) -> None:
        """Sets the delay used between async loading attempts."""
        try:
            self.__delay = float(new_delay)
        except Exception:
            raise TypeError("<'delay' type is not correct>")

    @property
    def data(self) -> dict[int, Chat | Bot | Model]:
        """Returns the archive data, reloading it if needed."""
        if self.__data_is_modified:
            self.__data = self.retrieve()
            self.__data_is_modified = False
        return self.__data

    @data.setter
    def data(self, new_data: dict[int, Chat | Bot | Model]) -> None:
        """Replaces the internal archive data."""
        if not isinstance(new_data, dict):
            raise TypeError("<'data' must be a dict>")
        self.__data = new_data

    @property
    def next_id(self) -> int:
        """Returns the next available integer id."""
        keys = self.data.keys()
        if not keys:
            return 0

        try:
            actual_ids = {int(k) for k in keys}
        except (TypeError, ValueError) as e:
            raise TypeError("<Archive contains non-integer IDs>") from e

        return max(actual_ids) + 1

    # -------- ACTIONS --------
    def get_ids(self, element: Chat | Bot | Model) -> list[int]:
        """
        Returns a list of ids that match the given element.
        """
        if not isinstance(element, (Chat, Bot, Model)):
            raise TypeError(f"<Invalid element type. Expected Chat | Bot | Model, got {type(element)}>")
        return [int(k) for k, v in self.data.items() if v == element]

    def has_id(self, identifier: int) -> bool:
        """
        Returns True if the id exists in the archive.
        """
        return int(identifier) in self.data

    def add(self, element: Chat | Bot | Model) -> None:
        """
        Adds an element under the next available id.
        """
        if not isinstance(element, (Chat, Bot, Model)):
            raise TypeError(f"<Invalid 'element' type. Expected Chat | Bot | Model, got {type(element)}>")
        self.data[self.next_id] = element

    def remove(self, element: list | tuple | int | Chat | Bot | Model, remove_type: str = "all") -> None:
        """
        Remove one or more entries from the archive—accepts an integer id,
        a domain object (Chat, Bot, Model), or an iterable of these; when an object maps to multiple ids,
        the remove_type parameter ("all", "first", "last") controls whether all matches, only the first,
        or only the last matching entry is deleted.
        """
        data = self.data

        # Iterable removal: reuse the same logic for each item
        if isinstance(element, (list, tuple)):
            if not all(isinstance(x, (int, Chat, Bot, Model)) for x in element):
                raise TypeError("<Unexpected object type inside iterable>")
            for item in element:
                self.remove(item, remove_type=remove_type)
            self.data = data
            return

        # Object removal by equality
        if isinstance(element, (Chat, Bot, Model)):
            selected_ids = self.get_ids(element)
            if not selected_ids:
                raise Exception(f"<The item does not match any id in the archive. element: {str(element)}>")
            match remove_type.lower().strip():
                case "all":
                    for _id in selected_ids:
                        del data[_id]
                case "first":
                    del data[selected_ids[0]]
                case "last":
                    del data[selected_ids[-1]]
                case _:
                    raise ValueError(f"<The entered 'remove_type' is not allowed: '{remove_type}'>")
            self.data = data
            return

        # Id removal
        try:
            identifier = int(element)
        except Exception:
            raise TypeError(f"<Unexpected element type: {type(element)}>")

        if not self.has_id(identifier):
            raise Exception(f"<Identifier not found. {identifier}>")

        del data[identifier]
        self.data = data




    # |=================================|
    # | -------- SAVING SYSTEM -------- |
    # |=================================|
    def save(self, path: str | None = None, include_secrets: bool = False) -> None:
        """
        Saves the current archive data into a .cwarchive binary file.
        """
        target_path = self.path if path is None else str(path)

        # Write atomically using a temporary file
        tmp_path = target_path + ".tmp"

        objects = self.data  # {id: obj}

        # Prepare records in a stable order (by id)
        items = sorted(objects.items(), key=lambda kv: int(kv[0]))

        with open(tmp_path, "wb") as f:
            # 1) Write header with placeholders
            header_info = self.__write_header_placeholder(f)

            # 2) Write records and collect index entries
            index_entries: list[dict[str, Any]] = []
            for object_id, obj in items:
                object_id_int = int(object_id)

                type_code = self.__type_code(obj)
                snapshot = self.__safe_freeze(obj, include_secrets=include_secrets)

                payload = self.__encode_payload(snapshot)
                checksum = self.__checksum32(payload)

                offset = f.tell()
                self.__write_record(
                    f=f,
                    type_code=type_code,
                    object_id=object_id_int,
                    rec_flags=0,
                    payload=payload,
                    checksum=checksum,
                )

                index_entries.append({
                    "object_id": object_id_int,
                    "type_code": type_code,
                    "rec_flags": 0,
                    "offset": offset,
                    "payload_len": len(payload),
                    "checksum": checksum,
                })

            # 3) Write index and patch header fields
            index_offset = f.tell()
            self.__write_index(f, index_entries)

            object_count = len(index_entries)
            self.__patch_header(
                f=f,
                header_info=header_info,
                index_offset=index_offset,
                object_count=object_count,
            )

        os.replace(tmp_path, target_path)


    # -------- HEADER HELPERS --------
    def __write_header_placeholder(self, f) -> dict[str, int]:
        """
        Writes a header with placeholder fields and returns patch offsets.
        """
        magic = b"cw"
        version = 1
        flags = 0

        # The header we write is 24 bytes:
        # 2 + 2 + 2 + 2 + 8 + 4 + 4 = 24
        header_len = 24
        metadata_len = 0

        f.write(magic)
        self.__write_u16(f, version)
        self.__write_u16(f, flags)
        self.__write_u16(f, header_len)

        index_offset_pos = f.tell()
        self.__write_u64(f, 0)

        object_count_pos = f.tell()
        self.__write_u32(f, 0)

        self.__write_u32(f, metadata_len)

        return {
            "index_offset_pos": index_offset_pos,
            "object_count_pos": object_count_pos,
        }

    def __patch_header(self, f, header_info: dict[str, int], index_offset: int, object_count: int) -> None:
        """
        Patches header placeholders after writing the file.
        """
        current = f.tell()

        # Patch index_offset
        f.seek(header_info["index_offset_pos"])
        self.__write_u64(f, index_offset)

        # Patch object_count
        f.seek(header_info["object_count_pos"])
        self.__write_u32(f, object_count)

        # Restore file pointer
        f.seek(current)


    # -------- RECORD HELPERS --------
    def __write_record(self, f, type_code: int, object_id: int, rec_flags: int, payload: bytes,
                       checksum: int) -> None:
        """
        Writes a single record to the file.
        """
        # RecordHeader:
        # type_code(u8), object_id(u32), rec_flags(u16), payload_len(u64), checksum(u32)
        self.__write_u8(f, type_code)
        self.__write_u32(f, object_id)
        self.__write_u16(f, rec_flags)
        self.__write_u64(f, len(payload))
        self.__write_u32(f, checksum)

        # Payload
        f.write(payload)

    def __write_index(self, f, entries: list[dict[str, Any]]) -> None:
        """
        Writes the index section at the end of the file.
        """
        f.write(b"IDX1")
        self.__write_u32(f, len(entries))

        for e in entries:
            self.__write_u32(f, int(e["object_id"]))
            self.__write_u8(f, int(e["type_code"]))
            self.__write_u16(f, int(e["rec_flags"]))
            self.__write_u64(f, int(e["offset"]))
            self.__write_u64(f, int(e["payload_len"]))
            self.__write_u32(f, int(e["checksum"]))
            self.__write_u8(f, 0)  # reserved


    # -------- SERIALIZATION HELPERS --------
    def __safe_freeze(self, obj: Any, include_secrets: bool = False) -> dict[str, Any]:
        """
        Creates a snapshot dict without secrets.
        """
        if hasattr(obj, "freeze") and callable(getattr(obj, "freeze")):
            try:
                return obj.freeze(include_secrets=include_secrets)  # type: ignore[misc]
            except TypeError:
                return obj.freeze()  # type: ignore[misc]

        raise TypeError(f"<Object does not support freeze(): {type(obj)}>")

    def __encode_payload(self, snapshot: dict[str, Any]) -> bytes:
        """
        Encodes a snapshot dict as UTF-8 JSON bytes.
        """
        # Compact JSON to reduce size
        text = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
        return text.encode("utf-8")


    # -------- TYPE AND CHECKSUM HELPERS --------
    def __type_code(self, obj: Any) -> int:
        """
        Returns a numeric type code for supported objects.
        """
        if isinstance(obj, Model):
            return 0
        if isinstance(obj, Bot):
            return 1
        if isinstance(obj, Chat):
            return 2
        if isinstance(obj, TextNode):
            return 3
        raise TypeError(f"<Unsupported object type: {type(obj)}>")

    def __checksum32(self, payload: bytes) -> int:
        """
        Computes a simple 32-bit checksum for payload bytes.
        """
        # Simple checksum: sum of bytes modulo 2^32
        return sum(payload) & 0xFFFFFFFF


    # -------- PRIMITIVE WRITERS --------
    @staticmethod
    def __write_u8(f, value: int) -> None:
        """
        Writes an unsigned 8-bit integer in little-endian.
        """
        f.write(int(value).to_bytes(1, "little", signed=False))

    @staticmethod
    def __write_u16(f, value: int) -> None:
        """
        Writes an unsigned 16-bit integer in little-endian.
        """
        f.write(int(value).to_bytes(2, "little", signed=False))

    @staticmethod
    def __write_u32(f, value: int) -> None:
        """
        Writes an unsigned 32-bit integer in little-endian.
        """
        f.write(int(value).to_bytes(4, "little", signed=False))

    @staticmethod
    def __write_u64(f, value: int) -> None:
        """
        Writes an unsigned 64-bit integer in little-endian.
        """
        f.write(int(value).to_bytes(8, "little", signed=False))




    # |============================|
    # | -------- RETRIEVE -------- |
    # |============================|
    def retrieve(
            self,
            path: str | None = None,
            api_key: str | None = None,
            api_key_provider: Optional[Callable[[int, int, dict[str, Any]], Optional[str]]] = None,
    ) -> dict[int, Any]:
        """
        Loads objects from a .cwarchive file.
        """
        api_key = self.api_key if api_key is None else api_key

        file_path = self.path if path is None else str(path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"<File not found: {file_path}>")

        # Return empty data if the file is empty
        if os.path.getsize(file_path) == 0:
            return {}

        payload_items = self.__read_cwarchive_payloads(file_path)

        if self.asynchronous:
            rebuilt = asyncio.run(
                self.__async_rebuild_objects(
                    payload_items=payload_items,
                    api_key=api_key,
                    api_key_provider=api_key_provider,
                )
            )
        else:
            rebuilt = self.__rebuild_objects_sync(
                payload_items=payload_items,
                api_key=api_key,
                api_key_provider=api_key_provider,
            )

        return rebuilt

    # -------- FILE PARSING (SEQUENTIAL) File parsing (sequential) --------
    def __read_cwarchive_payloads(self, file_path: str) -> list[dict[str, Any]]:
        """
        Reads headers, index, and payload bytes from the file.
        """
        if os.path.getsize(file_path) == 0:
            return []

        items: list[dict[str, Any]] = []

        with open(file_path, "rb") as f:
            magic = self.__read_exact(f, 2)
            if magic != b"cw":
                raise ValueError("<Invalid cwarchive: bad magic>")

            version = self.__read_u16(f)
            if version != 1:
                raise ValueError(f"<Unsupported cwarchive version: {version}>")

            _flags = self.__read_u16(f)
            header_len = self.__read_u16(f)

            index_offset = self.__read_u64(f)
            _object_count = self.__read_u32(f)
            metadata_len = self.__read_u32(f)

            # Skip metadata if present
            if metadata_len > 0:
                _ = self.__read_exact(f, metadata_len)

            # If header_len is larger than what we read, skip remaining header bytes
            already_read = 2 + 2 + 2 + 2 + 8 + 4 + 4 + metadata_len
            if header_len > already_read:
                _ = self.__read_exact(f, header_len - already_read)

            if index_offset <= 0:
                raise ValueError("<Invalid cwarchive: missing index offset>")

            # ----- index -----
            f.seek(index_offset)
            idx_magic = self.__read_exact(f, 4)
            if idx_magic != b"IDX1":
                raise ValueError("<Invalid cwarchive: bad index magic>")

            count = self.__read_u32(f)

            index_entries: list[dict[str, Any]] = []
            for _ in range(count):
                object_id = self.__read_u32(f)
                type_code = self.__read_u8(f)
                rec_flags = self.__read_u16(f)
                offset = self.__read_u64(f)
                payload_len = self.__read_u64(f)
                checksum = self.__read_u32(f)
                _reserved = self.__read_u8(f)

                index_entries.append({
                    "object_id": int(object_id),
                    "type_code": int(type_code),
                    "rec_flags": int(rec_flags),
                    "offset": int(offset),
                    "payload_len": int(payload_len),
                    "checksum": int(checksum),
                })

            # ----- records -----
            for e in index_entries:
                f.seek(e["offset"])

                type_code_r = self.__read_u8(f)
                object_id_r = self.__read_u32(f)
                rec_flags_r = self.__read_u16(f)
                payload_len_r = self.__read_u64(f)
                checksum_r = self.__read_u32(f)

                payload = self.__read_exact(f, payload_len_r)

                # Basic integrity checks (simple checksum)
                chk = self.__checksum32(payload)
                if chk != checksum_r:
                    raise ValueError(f"<Corrupted payload (id={object_id_r}): checksum mismatch>")

                # Optional: cross-check index vs record
                if int(object_id_r) != e["object_id"] or int(type_code_r) != e["type_code"]:
                    raise ValueError(f"<Index mismatch for record id={e['object_id']}>")

                items.append({
                    "object_id": int(object_id_r),
                    "type_code": int(type_code_r),
                    "rec_flags": int(rec_flags_r),
                    "payload": payload,
                })

        return items


    # -------- REBUILD OBJECTS (PARALLEL) --------
    def __chunk_items(self, items: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        """
        Splits items into small chunks for parallel reconstruction.
        """
        # You can tune this later. Keep it simple for now.
        step = 1 if len(items) < 50 else 3
        return [items[i:i + step] for i in range(0, len(items), step)]

    async def __async_rebuild_objects(
            self,
            payload_items: list[dict[str, Any]],
            api_key: str | None,
            api_key_provider: Optional[Callable[[int, int, dict[str, Any]], Optional[str]]],
    ) -> dict[int, Any]:
        """
        Rebuilds objects from payload items using parallel tasks.
        """
        chunks = self.__chunk_items(payload_items)

        tasks: Sequence[Awaitable[dict[int, Any]]] = [
            self.__async_rebuild_chunk(chunk, api_key=api_key, api_key_provider=api_key_provider)
            for chunk in chunks
        ]

        results = await asyncio.gather(*tasks)

        merged: dict[int, Any] = {}
        for part in results:
            merged.update(part)

        return merged

    async def __async_rebuild_chunk(
            self,
            chunk: list[dict[str, Any]],
            api_key: str | None,
            api_key_provider: Optional[Callable[[int, int, dict[str, Any]], Optional[str]]],
    ) -> dict[int, Any]:
        """
        Rebuilds a chunk in a worker thread to avoid blocking the event loop.
        """
        out: dict[int, Any] = {}

        for item in chunk:
            object_id = int(item["object_id"])
            type_code = int(item["type_code"])
            payload = item["payload"]

            # Run decode+thaw in a thread
            obj = await asyncio.to_thread(
                self.__decode_and_thaw,
                object_id,
                type_code,
                payload,
                api_key,
                api_key_provider,
            )
            out[object_id] = obj

        return out

    def __rebuild_objects_sync(
            self,
            payload_items: list[dict[str, Any]],
            api_key: str | None,
            api_key_provider: Optional[Callable[[int, int, dict[str, Any]], Optional[str]]],
    ) -> dict[int, Any]:
        """
        Rebuilds objects sequentially.
        """
        out: dict[int, Any] = {}
        for item in payload_items:
            object_id = int(item["object_id"])
            type_code = int(item["type_code"])
            payload = item["payload"]
            out[object_id] = self.__decode_and_thaw(
                object_id,
                type_code,
                payload,
                api_key,
                api_key_provider,
            )
        return out

    def __decode_and_thaw(
            self,
            object_id: int,
            type_code: int,
            payload: bytes,
            api_key: str | None,
            api_key_provider: Optional[Callable[[int, int, dict[str, Any]], Optional[str]]],
    ) -> Any:
        """
        Decodes JSON payload and rebuilds the object using thaw().
        """
        text = payload.decode("utf-8")
        snapshot = json.loads(text)

        # Optional per-object api key injection (not stored in archive)
        chosen_key: str | None = api_key
        if api_key_provider is not None:
            try:
                provided = api_key_provider(object_id, type_code, snapshot)
                if provided is not None:
                    chosen_key = str(provided)
            except Exception:
                # Keep it strict/simple: provider errors should fail fast
                raise

        # Type mapping
        if type_code == 0:
            # Model
            return Model.thaw(snapshot, api_key=chosen_key)
        if type_code == 1:
            # Bot
            return Bot.thaw(snapshot, api_key=chosen_key)
        if type_code == 2:
            # Chat
            return Chat.thaw(snapshot, api_key=chosen_key)
        if type_code == 3:
            # TextNode
            return TextNode.thaw(snapshot)

        raise TypeError(f"<Unsupported type_code: {type_code}>")


    # -------- PRIMITIVE READERS AND CHECKSUM --------
    @staticmethod
    def __read_exact(f, n: int) -> bytes:
        """
        Reads exactly n bytes or raises an error.
        """
        n = int(n)
        if n < 0:
            raise ValueError("<Invalid read size>")

        data = f.read(n)
        if data is None or len(data) != n:
            raise EOFError("<Unexpected end of file>")
        return data

    def __read_u8(self, f) -> int:
        """
        Reads an unsigned 8-bit integer in little-endian.
        """
        return int.from_bytes(self.__read_exact(f, 1), "little", signed=False)

    def __read_u16(self, f) -> int:
        """
        Reads an unsigned 16-bit integer in little-endian.
        """
        return int.from_bytes(self.__read_exact(f, 2), "little", signed=False)

    def __read_u32(self, f) -> int:
        """
        Reads an unsigned 32-bit integer in little-endian.
        """
        return int.from_bytes(self.__read_exact(f, 4), "little", signed=False)

    def __read_u64(self, f) -> int:
        """
        Reads an unsigned 64-bit integer in little-endian.
        """
        return int.from_bytes(self.__read_exact(f, 8), "little", signed=False)






def load(cw_string_object) -> Any:
    """
    Loads an object from its string representation.
    """
    try:
        return eval(cw_string_object)
    except Exception:
        print(cw_string_object)
        raise Exception("<The object entered cannot be converted. Invalid format.>")


async def async_load(cw_string_object) -> Any:
    """
    Loads an object from its string representation in a worker thread.
    """
    local_globals = dict(globals())
    try:
        return await asyncio.to_thread(eval, cw_string_object, local_globals)
    except Exception as e:
        raise Exception(f"<The object entered cannot be converted. Exception: {e}>")
