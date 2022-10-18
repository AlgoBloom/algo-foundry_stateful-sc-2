from pyteal import *

def game():
    # Write your code here
    monsterHealth = Btoi(Txn.application_args[0])
    handle_creation = Seq([
        Assert(monsterHealth >= Int(5)),
        # 5 pt of health to start
        App.globalPut(Bytes("Health"), monsterHealth),
        # initialize global state of the highest damage dealt to 0
        App.globalPut(Bytes("MaxDamage"), Int(0)),
        Return(Int(1))
    ])
        
    handle_optin = Seq([
        # should prevent player from making multiple opt in transactions
        Assert(App.optedIn(Txn.sender(),Txn.application_id())),
        # initialize local state of damage done to the monster to 0
        App.localPut(Txn.sender(), Bytes("Damage"), Int(0)),
        Return(Int(1))
    ])

    attack = Seq(
        #  each attack reduces hit points of monster by 2 
        App.globalPut(Bytes("HitPoints"), App.globalGet(Bytes("HitPoints"))-2),
        #  the players local state should keep track of the damage dealt to that monster 
        App.localPut(Txn.sender(), Bytes("DamageDone"), App.globalGet(Bytes("DamageDone")),
        Return(Int(1))
    )

    amountToSend = Btoi(Txn.application_args[1])
    send_algos = Seq([
        Assert(Txn.sender() == Global.creator_address()),
        Assert(amountToSend <= Int(1000000)),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: Txn.accounts[1],
            TxnField.amount: amountToSend,
        }),
        InnerTxnBuilder.Submit(),
        Return(Int(1))
    ])

    handle_noop = Seq(
        Assert(Global.group_size() == Int(1)),
        Cond(
    #  the contract will use the local state value to determine if this player did the most damage to the monster    
            [Txn.application_args[0] == Bytes("Attack"), attack_monster],
            [Txn.application_args[0] == Bytes("Reward"), reward_player]
        )
    )

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