from typing import Union, List, Optional

from pymodelio.validators import IterableValidator


class TupleValidator(IterableValidator):

    def __init__(self, elements_type: Union[type, List[type]] = None,
                 allow_empty: bool = True, nullable: bool = False, message: Optional[str] = None) -> None:
        super().__init__(expected_type=tuple, elements_type=elements_type, allow_empty=allow_empty, nullable=nullable,
                         message=message)
