from __future__ import annotations
import os

from typing import Any
from typing import Mapping, Dict, Sequence, Awaitable

import asyncio

# relative imports
from .Model import Model
from .Bot import Bot
from .Chat import Chat




class CWArchive(object):
    """
    # CWArchive
    
    ## Description
    Manages an archive of `Chat`, `Bot`, or `Model` objects from a given file path. Provides both synchronous and asynchronous methods for loading and saving data, as well as operations to add, remove, or retrieve items within the archive.
    """

    def __init__(self, path: str, asynchronous: bool = True, delay: float = 0.07) -> None:
        """
            # CWArchive
            
            ## Description
            Manages an archive of `Chat`, `Bot`, or `Model` objects from a given file path. Provides both synchronous and asynchronous methods for loading and saving data, as well as operations to add, remove, or retrieve items within the archive.

            ## Attributes
            ```python
            archive_path: str             # The file path used to store the archive.
            archive_data: dict            # Dictionary representing the archived items with integer IDs as keys.
            archive_id: int               # The next available ID for adding a new item to the archive.
            archive_delay: float          # The delay (in seconds) between asynchronous load operations.
            archive_asynchronous: bool    # Indicates whether the archive is loaded and saved asynchronously.
            ```

            ## Methods
            ```python
            __str__() -> str
                # Returns a user-friendly string representation of the archive in the format <Archive | path=...>.

            __repr__() -> str
                # Returns a developer-friendly string representation of the archive.

            __len__() -> int
                # Returns the number of items currently stored in the archive.

            __add__(other: Chat | Bot | Model)
                # Adds the given object to the archive and returns the updated archive.

            __sub__(other: int | Chat | Bot | Model)
                # Removes the specified item (by ID or object) from the archive and returns the updated archive.

            define(path: str, delay: float) -> None
                # Defines or updates the archive path and sets the delay for async operations.

            get_id_from_element(element: Chat | Bot | Model) -> list[int]
                # Retrieves all IDs corresponding to the specified element in the archive.

            is_valid_id(identifier: int) -> bool
                # Checks if the provided ID exists in the archive.

            add(element: Chat | Bot | Model) -> None
                # Adds a new element to the archive under the next available ID.

            remove(element: list | set | tuple | int | Chat | Bot | Model, remove_type: str | None = "all") -> None
                # Removes one or more elements from the archive by ID(s) or object(s). 
                # The 'remove_type' parameter determines whether to remove all matching IDs, the first matching ID, or the last.

            save() -> None
                # Saves the current archive data to the file, ordering items by their representation before writing.

            retrieve() -> dict[int, Any]
                # Loads and returns all items from the archive file. If asynchronous loading is enabled, items are loaded in chunks using asyncio.
            ```
            
            ---
            
            # __init__
            
            ## Description
            Initialize the CWArchive instance with a path, an asynchronous flag, and an optional delay.
            
            ## Parameters
            ```python
            path: str            # The file path to the archive
            asynchronous: bool   # Indicates whether the archive operates asynchronously
            delay: float         # Delay (in seconds) between asynchronous load operations
            ```
            
            ## Raises
            ```python
            TypeError  # Sollevato se 'asynchronous' non è un booleano
            ```
            
            ## Possible Error (Summary)
            Race conditions can occur when operating asynchronously with certain operations that are not thread-safe. This often manifests as an error during object loading.

            ### Why it happens
            - The underlying operations are not fully thread-safe.

            ### How to fix it
            - Increase the 'delay' value (e.g., start from 0.07s and adjust as needed).
            - If errors persist, disable asynchronous behavior by setting 'archive_asynchronous' to False. (this will slow down the loading time)
        """
        
        # path
        self.__path = path 
        
        # asynchronous
        if isinstance(asynchronous, bool):
            self.archive_asynchronous = asynchronous
        else:
            raise TypeError(f"<Unexcpected type for 'asynchronous'. Expected 'bool', got instead {type(asynchronous)}>")
        
        # delay
        self.__delay = delay
        
        # data
        self.__data = self.archive_data
        self.__data_is_modified = False
        
    
    # -------- MAGIC METHODS --------
    def __str__(self) -> str:
        """
        # __str__

        ## Description
        Return a human-readable string representation of the CWArchive instance, including the path of the archive.
        """

        return f"<Archive | path={self.__path}>"
    
    def __repr__(self) -> str:
        """
        # __repr__

        ## Description
        Return an official string representation of the CWArchive instance, suitable for debugging or logging.
        """

        return f"Archive(path={repr(self.__path)})"
    
    def __len__(self) -> int:
        """
            # __len__

            ## Description
            Return the number of elements currently stored in the archive.
        """

        return len(self.archive_data)
    
    def __add__(self, other: Chat | Bot | Model):
        """
            # __add__

            ## Description
            Add a Chat, Bot, or Model object to the archive. The object is stored under the next available ID.

            ## Parameters
            ```python
            other: Chat | Bot | Model  # The object to be added to the archive
            ```

            ## Raises
            ```
            TypeError  # Raised if 'other' is not a Chat, Bot, or Model instance
            ```
        """

        if not isinstance(other, Chat | Bot | Model):
            raise TypeError(f"<Unexpected type. Expected 'Chat' or 'Bot' or 'Model', instead got {type(other)}>")
        self.add(other)
        return self
    
    def __sub__(self, other: int | Chat | Bot | Model):
        """
        # __sub__

        ## Description
        Remove an element from the archive by either its integer ID or by a Chat, Bot, or Model instance.
        - If 'other' is an integer, it removes the element with that ID.
        - If 'other' is a Chat, Bot, or Model object, it removes the matching element.

        ## Parameters
        ```python
        other: int | Chat | Bot | Model  # The identifier or object to remove from the archive
        ```

        ## Raises
        ```
        TypeError  # Raised if 'other' is neither an integer nor a Chat/Bot/Model
        ```
    """

        if isinstance(other, int):
            self.remove(element=other)
            return self
        elif isinstance(other, Chat | Bot | Model):
            self.remove(element=other)
            return self
        else:
            raise TypeError(f"<Unexpected type. Expected 'int' or 'Chat' or 'Bot' or 'Model', instead got {type(other)}>")
    
    def __enter__(self, *args, **kwargs):
        return self
    
    def __exit__(self, *args, **kwargs) -> None:
        self.save()
    
    # -------- GET --------
    # ARCHIVE_PATH
    @property
    def archive_path(self) -> str:
        """
            # archive_path (getter)

            ## Description
            Get the path where the archive file is stored.
        """

        return self.__path
    @archive_path.setter
    def archive_path(self, new_path: str) -> None:
        """
            # archive_path (setter)

            ## Description
            Update the archive's file path. This marks the data as modified so that it will be reloaded next time it is accessed.

            ## Parameters
            ```python
            new_path: str  # The new path for the archive file
            ```
        """
        
        if os.path.exists(new_path):
            self.__path = new_path
            self.save()
        else:
            raise FileExistsError(f"<File '{new_path}' does not exixts>")
        
        # move the archive to the new path
        self.__path = new_path
        self.__data_is_modified = True
    
    # ARCHIVE_ASYNCHRONOUS
    @property
    def archive_asynchronous(self) -> bool:
        """
            # archive_asynchronous (getter)

            ## Description
            Get the current asynchronous flag, indicating whether the archive operates in asynchronous mode.
        """

        return self.__asynchronous
    @archive_asynchronous.setter
    def archive_asynchronous(self, new_asynchronous) -> None:
        """
            # archive_asynchronous (setter)

            ## Description
            Enable or disable asynchronous behavior for the archive.

            ## Parameters
            ```python
            new_asynchronous: bool  # True to enable asynchronous mode, False otherwise
            ```

            ## Raises
            ```
            TypeError  # Raised if 'new_asynchronous' is not a bool
            ```
        """

        if isinstance(new_asynchronous, bool):
            self.__asynchronous = new_asynchronous
        else:
            raise TypeError(f"<Unexcpected type for 'asynchronous'. Expected 'bool', got instead {type(new_asynchronous)}>")
    
    # ARCHIVE_DATA
    @property
    def archive_data(self) -> dict:
        """
            # archive_data (getter)

            ## Description
            Get the archive's data as a dictionary. If the data has been marked as modified, 
            this property triggers a reload from the file before returning the data.
        """

        if "_CWArchive__data_is_modified" not in self.__dir__():
            self.__data_is_modified = True
        
        if self.__data_is_modified:
            self.__data = self.retrieve()
            self.__data_is_modified = False
        
        return self.__data
    @archive_data.setter
    def archive_data(self, new_archive_data: dict) -> None:
        """
            # archive_data (setter)

            ## Description
            Set (replace) the current archive data with a new dictionary.

            ## Parameters
            ```python
            new_archive_data: dict  # The new data to store in the archive
            ```
        """

        self.__data = new_archive_data
    
    # ARCHIVE_ID
    @property
    def archive_id(self) -> int:
        """
            # archive_id (getter)

            ## Description
            Retrieve the next available integer ID that can be used to store a new element in the archive.
        """

        keys = self.archive_data.keys()
        if not keys:
            return 0

        try:
            actual_ids = {int(k) for k in keys}
        except (TypeError, ValueError) as e:
            raise TypeError("<Archive contains non-integer IDs>") from e

        return max(actual_ids) + 1


    # ARCHIVE_DELAY
    @property
    def archive_delay(self) -> float:
        """
            # archive_delay (getter)

            ## Description
            Get the current delay (in seconds) used between asynchronous loading operations.
        """

        return self.__delay
    @archive_delay.setter
    def archive_delay(self, new_delay: float) -> None:
        """
            # archive_delay (setter)

            ## Description
            Set the new delay (in seconds) for asynchronous loading operations.

            ## Parameters
            ```python
            new_delay: float  # The delay value in seconds
            ```

            ## Raises
            ```
            TypeError  # Raised if 'new_delay' cannot be cast to float
            ```
        """

        try:
            self.__delay: float = float(new_delay)
        except:
            raise TypeError("<'new_delay' type is not correct>")
    
    
    # -------- ACTIONS --------
    def get_id_from_element(self, element: Chat | Bot | Model) -> list[int]:
        """
            # get_id_from_element

            ## Description
            Retrieve a list of integer IDs corresponding to the given element (Chat, Bot, or Model). 
            If the same element is stored multiple times, multiple IDs may be returned.

            ## Parameters
            ```python
            element: Chat | Bot | Model  # The element to look up in the archive
            ```
        """

        ids: list = list()
        for k, v in self.archive_data.items():
            ids.append(k) if v == element else None
        
        return ids
    
    
    def is_valid_id(self, identifier: int) -> bool:
        """
            # is_valid_id

            ## Description
            Check if the provided integer ID exists in the archive.

            ## Parameters
            ```python
            identifier: int  # The ID to check
            ```
        """

        return identifier in list(self.archive_data.keys())
    
    
    def add(self, element: Chat | Bot | Model) -> None:
        """
            # add

            ## Description
            Add a Chat, Bot, or Model object to the archive under the next available ID.

            ## Parameters
            ```python
            element: Chat | Bot | Model  # The object to add to the archive
            ```

            ## Raises
            ```
            TypeError  # Raised if 'element' is not a Chat, Bot, or Model
            ```
        """

        if not isinstance(element, Chat | Bot | Model):
            raise TypeError(f"<Invalid 'element' type. Expected 'Chat | Bot | Model', got instead {type(element)}>")
        
        self.archive_data[self.archive_id] = element
    
    
    def remove(self, element: list | tuple | int | Chat | Bot | Model, remove_type: str = "all") -> None:
        """
            # remove

            ## Description
            Remove one or more elements from the archive. Elements can be specified by:
            - A single integer ID
            - A single Chat, Bot, or Model
            - An iterable (list, set, tuple) of IDs or Chat/Bot/Model instances.
            The 'remove_type' parameter can be used to remove all matching items, or only the first/last match.

            ## Parameters
            ```python
            element: list | set | tuple | int | Chat | Bot | Model  # The item(s) or ID(s) to remove
            remove_type: str | None = "all"                          # Removal strategy: "all", "first", or "last"
            ```

            ## Raises
            ```
            TypeError  # Raised if 'element' has invalid types
            Exception  # Raised if the element or ID to remove is not found
            ```
        """

        data = self.archive_data
        
        if isinstance(element, list | tuple): # Check if 'element' is an iterable
            if all([isinstance(identifier, int | Chat | Bot | Model) for identifier in element]): # Check if every item inside the iterable is int | Chat | Bot | Model.
                for index, is_type in enumerate([isinstance(identifier, Chat | Bot | Model) for identifier in element]):
                    obj = element[index]
                    if is_type:
                        selected_ids = self.get_id_from_element(element=obj)
                        if selected_ids:
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
                        else:
                            raise Exception(f"<The item does not match any id in the archive. element: {str(obj)}>")
                    else:
                        if not self.is_valid_id(identifier=obj):
                            raise Exception(f"<Identifier not found. {obj}>")
                        del data[obj]
            else:
                raise TypeError(f"<Unexpected object type inside the iterable. Excpected 'int | Chat | Bot | Model'>")
        elif isinstance(element, Chat | Bot | Model):
            selected_ids = self.get_id_from_element(element=element)
            if selected_ids:
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
            else:
                raise Exception(f"<The item does not match any id in the archive. element: {str(element)}>")
        else:
            try:
                element = int(element)
                if not self.is_valid_id(identifier=element):
                    raise Exception(f"<Identifier not found. {element}>")
                del data[element]
            except:
                raise TypeError(f"<Unexpected object type. Excpected 'list[int | Chat | Bot | Model] | set[int | Chat | Bot | Model] | tuple[int | Chat | Bot | Model] | int | Chat | Bot | Model', got instead {type(element)}>")
        
        self.archive_data = data
        
    
    def save2(self) -> None:
        """
            # save

            ## Description
            Save the current archive data to the file in sorted order. 
        """

        data = {k: v for k, v in sorted(self.archive_data.items(), key=lambda item: item[1])}
        with open(self.archive_path, "w") as f:
            for ID, obj in data.items():
                data[ID] = repr(obj)
            
            f.write(repr(data))
            self.__data_is_modified = True


    def save(self, default_api_key: str):
        objects = [Model, Bot, Chat]

        data = {k: v for k, v in sorted(self.archive_data.items(), key=lambda item: item[1])}

        header = [ord("c"), ord("w"), len(data).to_bytes(2), len(bytes(default_api_key, "utf-8")).to_bytes(3), bytes(default_api_key, "utf-8")]

        body = []

        footer = [ord("c"), ord("w")]

    def __chunk_data(self, dictionary: dict) -> list[dict]:
        """
            # __chunk_data

            ## Description
            Split a dictionary into smaller dictionaries (chunks) of a specified maximum size.
            Used for batching data when loading it asynchronously.

            ## Parameters
            ```python
            dictionary: dict  # The dictionary to split into chunks
            step: int         # The size of each chunk
            ```
        """
        if self: pass

        dictionary_list: list = list(dictionary.items())

        length = len(dictionary_list)
        #step = int((7/95)*length + (50/19))
        step = 1 if length < 100 else 3

        return [dict(dictionary_list[i:i+step]) for i in range(0, len(dictionary_list), step)]


    async def __async_load_chunk(
        self,
        chunk: Mapping[int, str]
    ) -> Dict[int, Chat]:
        """
        Load and reconstruct objects asynchronously from a chunk of string representations.
        Returns a dict mapping IDs to Chat instances.
        """

        loaded: Dict[int, Chat] = {}
        for k, v in chunk.items():
            for attempt in range(6):
                try:
                    if attempt > 0:
                        await asyncio.sleep(self.archive_delay)
                    loaded[k] = await async_load(v)
                    break
                except Exception as e:
                    if attempt == 5:
                        raise Exception(
                            f"<Error loading (id={k}): {e}>"
                        ) from e
        return loaded

    async def __async_retrieve(
        self,
        chunked_data: Sequence[Mapping[int, str]]
    ) -> Dict[int, Chat]:
        """
        Asynchronously load and reconstruct objects from multiple chunks in parallel.
        """

        tasks: Sequence[Awaitable[Dict[int, Chat]]] = [
            self.__async_load_chunk(chunk) for chunk in chunked_data
        ]
        results = await asyncio.gather(*tasks)
        merged: Dict[int, Chat] = {}
        for part in results:
            merged.update(part)
        return merged
    
    
    
    def retrieve(self) -> dict[int, Chat | Bot | Model]:
        """
            # retrieve

            ## Description
            Read the archive file from disk and reconstruct all stored objects. 
            If asynchronous mode is enabled, the data is split into chunks for parallel loading; 
            otherwise, the loading is performed sequentially.

            ## Raises
            ```
            TypeError   # Raised if the archive file contains data of an invalid type
            Exception   # Raised if the archive format is invalid or if loading fails
            ```
        """

        with open(self.archive_path, "r") as f:
            str_data: str = f.read()
        
        try:
            if str_data:
                data: dict[int, Any] = eval(str_data)   # {int: 'Chat', int: 'Chat', ...}
                
                if self.archive_asynchronous: # if 
                    chunked_data = self.__chunk_data(dictionary=data)
                    data = asyncio.run(self.__async_retrieve(chunked_data=chunked_data))
                else:
                    for k, v in data.items():
                        data[k] = load(v)
                return data
            else:
                return {}
        except TypeError:
            raise TypeError(f"<Invalid type>")
        except Exception as e:
            raise Exception(f"<Invalid archive format. {e}>")



class Loom(object):
    def __init__(self, *args, name: str = "Loom", strands: list[Bot] | None = None, flowchart: Any | None = None, **kwargs) -> None:
        self.name = name
        self.flowchart = flowchart
        self.strands = strands if strands else []

        raise NotImplemented(str(args) + str(kwargs))
    
    @property
    def name(self) -> str:
        return self.__name
    @name.setter
    def name(self, new_name: str = "Loom") -> None:
        self.__name = str(new_name)
        
    @property
    def strands(self) -> list[Bot]:
        return self.__strands
    @strands.setter
    def strands(self, new_strands: list[Bot]) -> None:
        self.__strands = new_strands
        
    @property
    def flowchart(self) -> Any | None:
        return self.__flowchart
    @flowchart.setter
    def flowchart(self, new_flowchart: Any) -> None:
        self.__flowchart = new_flowchart
    
    async def weave(self, request) -> None:
        ...




def load(cw_string_object) -> Any:
    """
    Args:
        cw_string_object (_type_): _description_

    Raises:
        Exception: _description_

    Returns:
        Any: _description_
    """
    
    try:
        return eval(cw_string_object)
    except:
        print(cw_string_object)
        raise Exception("<The object entered cannot be converted to a chatweaver object. Invalid format.>")


async def async_load(cw_string_object) -> Any:
    """
    Args:
        cw_string_object (_type_): _description_

    Raises:
        Exception: _description_

    Returns:
        Any: _description_
    """
    local_globals = dict(globals())
    
    try:
        return await asyncio.to_thread(eval, cw_string_object, local_globals)
    except Exception as e:
        raise Exception(f"<The object entered cannot be converted to a chatweaver object. Invalid format. Exception: {e}>")