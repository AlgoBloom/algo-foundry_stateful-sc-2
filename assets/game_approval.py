from pyteal import *

def game():
    # Write your code here
    handle_creation = Return(Int(1)) # need this:
                                     # 5pt health points start
                                     # initialize global state of the highest damage dealt to 0
    handle_optin = Return (Int(1)) # need this: 
                                   # initialize local state of damage done to the monster to 0
                                   # should prevent player from making multiple opt in transactions
    handle_noop = Return(Int(1))  # need this: 
                                  #  each attack reduces hit points of monster by 2 
                                  #  the players local state should keep track of the damage dealt to that monster 
                                  #  the contract will use the local state value to determine if this player did the most damage to the monster    
    handle_closeout = Return(Int(1))
    handle_updateapp = Return(Int(0))
    handle_deleteapp = Return(Int(1))

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )

    return program

if __name__ == "__main__":
    print(compileTeal(game(), mode=Mode.Application, version=6))