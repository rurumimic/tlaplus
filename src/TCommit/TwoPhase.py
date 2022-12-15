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

def records(*s): # k, v, ...
    return frozendict(zip(*[iter(s)]*2)) # frozendict({k: v, ...})

def sets(_frozendict): # frozendict({k: v, ...})
    return frozenset({_frozendict})

def EXCEPT(_sets, key, value):
    """
    sets: [{'r1': 'working'}, {'r2': 'working'},  {'r3': 'working'}]
    key: 'r1'
    value: 'prepared'
    """
    prev = next(x for x in _sets if key in x).value() # 'working'
    # [{'r1': 'working'}, {'r2': 'working'}, {'r3': 'working'}] - [{r1: 'working'}]
    _sets -= sets(records(key, prev))
    # [{'r2': 'working'}, {'r3': 'working'}] + [{r1: 'prepared'}]
    _sets |= sets(records(key, value))
    return _sets # [{r1: 'prepared'}, {r2: 'working'}, {r3: 'working'}]

def UNCHANGED(rm_state, tm_state, tm_prepared, messages):
    global rmState, tmState, tmPrepared, msgs
    global _rmState, _tmState, _tmPrepared, _msgs
    if rm_state: _rmState = rmState
    if tm_state: _tmState = tmState
    if tm_prepared: _tmPrepared = tmPrepared
    if messages: _msgs = msgs

def canCommit():
    global RM, rmState
    for rm in RM:
        rm_state = next(x for x in rmState if rm in x).value()
        if rm_state == "prepared" or rm_state == "committed":
            continue
        else:
            return False
    return True

def notCommitted():
    global RM, rmState
    for rm in RM:
        rm_state = next(x for x in rmState if rm in x).value()
        if rm_state != "committed":
            continue
        else:
            return False
    return True

def Prepare(r):
    global rmState, _rmState
    rm_state = next(x for x in rmState if r in x).value() # working / prepared / committed / aborted
    if rm_state == "working":
        _rmState = EXCEPT(rmState, r, "prepared")

def Decide(r):
    global rmState, _rmState
    rm_state = next(x for x in rmState if r in x).value() # working / prepared / committed / aborted
    if rm_state == "prepared" and canCommit():
        _rmState = EXCEPT(rmState, r, "committed")
    elif (rm_state == "working" or rm_state == "prepared") and notCommitted():
        _rmState = EXCEPT(rmState, r, "aborted")


def TPInit():
    global rmState, tmState, tmPrepared, msgs
    global _rmState, _tmState, _tmPrepared, _msgs
    rmState = frozenset({frozendict({ x: "working" }) for x in RM})
    # frozenset({
    #   frozendict.frozendict({'r3': 'working'}), 
    #   frozendict.frozendict({'r1': 'working'}), 
    #   frozendict.frozendict({'r2': 'working'})
    # })
    tmState = "init"
    tmPrepared = frozenset({})
    msgs = frozenset({})
    UNCHANGED('rmState', 'tmState', 'tmPrepared', 'msgs')

def TMRcvPrepared(r):
    global rmState, tmState, tmPrepared, msgs
    global _rmState, _tmState, _tmPrepared, _msgs
    if tmState == "init":
        if sets(records("type", "Prepared", "rm", r)).issubset(msgs):
            _tmPrepared = tmPrepared | frozenset({r})
            UNCHANGED('rmState', 'tmState', None, 'msgs')

def TMCommit():
    global rmState, tmState, tmPrepared, msgs
    global _rmState, _tmState, _tmPrepared, _msgs
    if tmState == "init":
        if tmPrepared == frozenset(RM):
            _tmState = "done"
            _msgs = msgs | sets(records("type", "Commit"))
            UNCHANGED('rmState', None, 'tmPrepared', None)

def TMAbort():
    global rmState, tmState, tmPrepared, msgs
    global _rmState, _tmState, _tmPrepared, _msgs
    if tmState == "init":
        _tmState = "done"
        _msgs = msgs | sets(records("type", "Abort"))
        UNCHANGED('rmState', None, 'tmPrepared', None)

def RMPrepare(r): # r1 / r2 / r3
    global rmState, tmState, tmPrepared, msgs
    global _rmState, _tmState, _tmPrepared, _msgs
    rm_state = next(x for x in rmState if r in x).value() # working / prepared / committed / aborted
    if rm_state == "working":
        _rmState = EXCEPT(rmState, r, "prepared")
        _msgs = msgs | sets(records("type", "Prepared", "rm", r))
        UNCHANGED(None, 'tmState', 'tmPrepared', None)

def RMChooseToAbort(r): # r1 / r2 / r3
    global rmState, tmState, tmPrepared, msgs
    global _rmState, _tmState, _tmPrepared, _msgs
    rm_state = next(x for x in rmState if r in x).value() # working / prepared / committed / aborted
    if rm_state == "working":
        _rmState = EXCEPT(rmState, r, "aborted")
        UNCHANGED(None, 'tmState', 'tmPrepared', 'msgs')

def RMRcvCommitMsg(r): # r1 / r2 / r3
    global rmState, tmState, tmPrepared, msgs
    global _rmState, _tmState, _tmPrepared, _msgs
    if sets(records("type", "Commit")).issubset(msgs):
        _rmState = EXCEPT(rmState, r, "committed")
        UNCHANGED(None, 'tmState', 'tmPrepared', 'msgs')

def RMRcvAbortMsg(r): # r1 / r2 / r3
    global rmState, tmState, tmPrepared, msgs
    global _rmState, _tmState, _tmPrepared, _msgs
    if sets(records("type", "Abort")).issubset(msgs):
        _rmState = EXCEPT(rmState, r, "aborted")
        UNCHANGED(None, 'tmState', 'tmPrepared', 'msgs')

def Next():
    global rmState, tmState, tmPrepared, msgs
    global _rmState, _tmState, _tmPrepared, _msgs
    print('rmState\n', rmState, '\n', _rmState)
    print('tmState\n', tmState, '\n', _tmState)
    print('tmPrepared\n', tmPrepared, '\n', _tmPrepared)
    print('msgs\n', msgs, '\n', _msgs)
    rmState = _rmState
    tmState = _tmState
    tmPrepared = _tmPrepared
    msgs = _msgs


#####################
# Scenario 1
TPInit()

RMPrepare("r1")
Next()
RMPrepare("r2")
Next()
RMPrepare("r3")
Next()

TMRcvPrepared("r1")
Next()
TMRcvPrepared("r2")
Next()
TMRcvPrepared("r3")
Next()

TMCommit()
Next()

RMRcvCommitMsg("r1")
Next()
RMRcvCommitMsg("r2")
Next()
RMRcvCommitMsg("r3")
Next()

##############
# Scenario 2
TPInit()
RMPrepare("r1")
Next()

TMRcvPrepared("r1")
Next()

RMChooseToAbort("r2")
Next()
RMChooseToAbort("r3")
Next()

TMAbort()
Next()

RMRcvAbortMsg("r1")
Next()

##############

rmState
tmState
tmPrepared
msgs
