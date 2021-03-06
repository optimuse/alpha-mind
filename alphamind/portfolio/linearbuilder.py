# -*- coding: utf-8 -*-
"""
Created on 2017-5-5

@author: cheng.li
"""

import numpy as np
from typing import Tuple
from typing import Union
from alphamind.cython.optimizers import LPOptimizer


def linear_build(er: np.ndarray,
                 lbound: Union[np.ndarray, float],
                 ubound: Union[np.ndarray, float],
                 risk_constraints: np.ndarray,
                 risk_target: Tuple[np.ndarray, np.ndarray],
                 turn_over_target: float = None,
                 current_position: np.ndarray = None) -> Tuple[str, np.ndarray, np.ndarray]:
    er = er.flatten()
    n, m = risk_constraints.shape

    if not risk_target:
        risk_lbound = -np.inf * np.ones((m, 1))
        risk_ubound = np.inf * np.ones((m, 1))
    else:
        risk_lbound = risk_target[0].reshape((-1, 1))
        risk_ubound = risk_target[1].reshape((-1, 1))

    if isinstance(lbound, float):
        lbound = np.ones(n) * lbound

    if isinstance(ubound, float):
        ubound = np.ones(n) * ubound

    if not turn_over_target:
        cons_matrix = np.concatenate((risk_constraints.T, risk_lbound, risk_ubound), axis=1)
        opt = LPOptimizer(cons_matrix, lbound, ubound, -er)

        status = opt.status()

        if status == 0:
            status = 'optimal'

        return status, opt.feval(), opt.x_value()
    else:
        current_position = current_position.reshape((-1, 1))

        # we need to expand bounded condition and constraint matrix to handle L1 bound
        lbound = np.concatenate((lbound, np.zeros(n)), axis=0)
        ubound = np.concatenate((ubound, np.inf * np.ones(n)), axis=0)

        risk_lbound = np.concatenate((risk_lbound, [[0.]]), axis=0)
        risk_ubound = np.concatenate((risk_ubound, [[turn_over_target]]), axis=0)

        risk_constraints = np.concatenate((risk_constraints.T, np.zeros((m, n))), axis=1)
        er = np.concatenate((er, np.zeros(n)), axis=0)

        turn_over_row = np.zeros(2 * n)
        turn_over_row[n:] = 1.
        risk_constraints = np.concatenate((risk_constraints, [turn_over_row]), axis=0)

        turn_over_matrix = np.zeros((2 * n, 2 * n))
        for i in range(n):
            turn_over_matrix[i, i] = 1.
            turn_over_matrix[i, i + n] = -1.
            turn_over_matrix[i + n, i] = 1.
            turn_over_matrix[i + n, i + n] = 1.

        risk_constraints = np.concatenate((risk_constraints, turn_over_matrix), axis=0)

        risk_lbound = np.concatenate((risk_lbound, -np.inf * np.ones((n, 1))), axis=0)
        risk_lbound = np.concatenate((risk_lbound, current_position), axis=0)

        risk_ubound = np.concatenate((risk_ubound, current_position), axis=0)
        risk_ubound = np.concatenate((risk_ubound, np.inf * np.ones((n, 1))), axis=0)

        cons_matrix = np.concatenate((risk_constraints, risk_lbound, risk_ubound), axis=1)
        opt = LPOptimizer(cons_matrix, lbound, ubound, -er)

        status = opt.status()

        if status == 0:
            status = 'optimal'

        return status, opt.feval(), opt.x_value()[:n]


if __name__ == '__main__':
    n = 5
    lb = np.zeros(n)
    ub = 4. / n * np.ones(n)
    er = np.random.randn(n)
    current_pos = np.random.randint(0, n, size=n)
    current_pos = current_pos / current_pos.sum()
    turn_over_target = 0.1

    cons = np.ones((n, 1))
    risk_lbound = np.ones(1)
    risk_ubound = np.ones(1)

    status, fvalue, x_values = linear_build(er,
                                            lb,
                                            ub,
                                            cons,
                                            (risk_lbound, risk_ubound),
                                            turn_over_target,
                                            current_pos)

    print(status)
    print(fvalue)
    print(x_values)
    print(current_pos)

    print(np.abs(x_values - current_pos).sum())
