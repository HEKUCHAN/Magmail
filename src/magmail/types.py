from typing import Any, Callable, Dict, List, Optional, Tuple, Union


FILTER_CONTENTS_TYPE = Union[str, List[str]]
CUSTOM_FUNCTIONS_DICT_TYPE = Dict[str, Optional[Callable[[str], Any]]]
CUSTOM_FUNCTIONS_ROOT_DICT_TYPE = Dict[str, CUSTOM_FUNCTIONS_DICT_TYPE]


ADDRESS_TYPE = Tuple[str, str]
ADDRESS_HEADER_TYPE = Union[str, ADDRESS_TYPE]
HEADER_TYPE = Union[str, ADDRESS_TYPE, List[ADDRESS_HEADER_TYPE]]
