from copy import deepcopy

from frozendict import frozendict

RM = {"r1", "r2", "r3"}

init_rm_state = frozenset({ frozendict({ "type": t, "rm": rm }) for t in { "Prepared" } for rm in RM })
# frozenset({
#   frozendict.frozendict({'type': 'Prepared', 'rm': 'r2'}),
#   frozendict.frozendict({'type': 'Prepared', 'rm': 'r3'}), 
#   frozendict.frozendict({'type': 'Prepared', 'rm': 'r1'})
# })

next_rm_state = frozenset({ frozendict({ "type": t }) for t in { "Commit", "Abort" } })
# frozenset({
#   frozendict.frozendict({'type': 'Commit'}), 
#   frozendict.frozendict({'type': 'Abort'})
# })

Messages = frozenset.union(init_rm_state, next_rm_state)
# frozenset({
#   frozendict.frozendict({'type': 'Prepared', 'rm': 'r1'}), 
#   frozendict.frozendict({'type': 'Prepared', 'rm': 'r2'}), 
#   frozendict.frozendict({'type': 'Commit'}), 
#   frozendict.frozendict({'type': 'Prepared', 'rm': 'r3'}), 
#   frozendict.frozendict({'type': 'Abort'})
# })

Messages

# TPInit
rmState = frozenset({ frozendict({ x: "working" }) for x in RM })
# frozenset({
#   frozendict.frozendict({'r3': 'working'}), 
#   frozendict.frozendict({'r1': 'working'}), 
#   frozendict.frozendict({'r2': 'working'})
# })
tmState = "init"
tmPrepared = frozenset({})
msgs = frozenset({})


# RMPrepare(r)
_rmState = deepcopy(rmState)
_msgs = deepcopy(msgs)
for r in RM:  
    rm = list(filter(lambda x: r in x, rmState))[0]
    if rm[r] == "working":
        _rmState = _rmState.difference(frozenset({rm})).union({frozendict({ r: "prepared"})})
        _msgs = _msgs.union(frozenset({ frozendict({ "type": t, "rm": rm }) for t in { "Prepared" } for rm in [r] }))
        tmPrepared = tmPrepared
        tmState = tmState
        print(r, _rmState, _msgs)

# TMRcvPrepared(r)
for r in RM:
    if tmState == "init":
        if frozenset({"type": "Prepared", "rm": r}) in msgs:
            tmPrepared = frozenset.union(tmPrepared, frozenset({r}))
            rmState = rmState
            tmState = tmState
            msgs = msgs

_rmState
_msgs