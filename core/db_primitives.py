from typing import List, Optional, Tuple


class CoreField:
    """Core Field."""
    sql_type: type
    name: str
    doc: Optional[str]
    primary_key: Optional[bool]
    foreign_key: Optional[str]
    nullable: Optional[bool]
    unique: Optional[bool]
    table_related: Optional[str]

    def __init__(
        self,
        sql_type,
        name,
        doc="",
        primary_key=False,
        foreign_key=None,
        nullable=True,
        unique=False,
        default=None,
        table_related=None,
        **kwargs
    ):

        self.sql_type = sql_type
        self.name = name
        self.doc = doc
        self.foreign_key = foreign_key
        self.default = default
        self.primary_key = primary_key

        if primary_key:
            self.nullable = False
            self.unique = True
        else:
            self.nullable = nullable
            self.unique = unique

        self.table_related = table_related
        self.spec_params = kwargs


class CoreModel:
    """Core Model."""
    tablename: str
    fields: List[
        CoreField,
    ]
    doc: str
    unique_together: Tuple[Tuple[str, ]]

    def __init__(
        self,
        tablename: str,
        fields: List[
            CoreField,
        ],
        doc: str = "Generated By ORM Combine",
        unique_together: Tuple[Tuple[str, ]] = ()
    ):
        self.tablename = tablename
        self.fields = fields
        for field in fields:
            field.table_related = self.tablename
            setattr(self, field.name, field)
        self.doc = doc
        self.unique_together = unique_together

    @property
    def __doc__(self):
        return self.doc
