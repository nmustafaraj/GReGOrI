from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, order=True)
class StableIdentity:
    assembly: str
    accession: str
    start: int
    end: int
    def __post_init__(self):
        if not self.assembly or not self.accession:
            raise ValueError('Assembly and sequence accession are required.')
        if self.start < 0 or self.end <= self.start:
            raise ValueError(f'Invalid 0-based half-open interval {self.start}:{self.end}.')
    @property
    def value(self):
        return f'{self.assembly}|{self.accession}|{self.start}|{self.end}'

def stable_id(assembly, accession, start, end):
    return StableIdentity(str(assembly), str(accession), int(start), int(end)).value
