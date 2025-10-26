# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations
import random
from typing import Tuple, List
from dataclasses import dataclass
from red_teaming.analysis.eval_awareness import salted_canary, wrap_prompt

@dataclass
class EvalMasker:
    secret: bytes
    strategies: List[str]
    noise_chars: List[str]

    def mask(self, task_id: str, prompt: str, nonce: int) -> Tuple[str, str, str]:
        strat = random.choice(self.strategies) if self.strategies else "fallback"
        salt = salted_canary(self.secret, task_id, strat, nonce)
        wrapped, mask_id = wrap_prompt(prompt, strat, salt, self.noise_chars)
        return wrapped, mask_id, salt
