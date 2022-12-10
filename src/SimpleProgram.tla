--------------------------- MODULE SimpleProgram ---------------------------
EXTENDS Integers
VARIABLES i, pc   

Init == (pc = "start") /\ (i = 0)

Pick == /\ pc = "start"  
        /\ i' \in 0..1000
        /\ pc' = "middle"

Add1 == /\ pc = "middle" 
        /\ i' = i + 1
        /\ pc' = "done"  
           
Next == Pick \/ Add1

=============================================================================
\* Modification History
\* Last modified Sat Dec 10 12:58:26 KST 2022 by dodo
\* Created Sat Dec 10 12:57:32 KST 2022 by dodo
